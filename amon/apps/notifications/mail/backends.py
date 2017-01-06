import smtplib
import threading
import ssl

from django.core.mail.utils import DNS_NAME
from django.core.mail.backends.smtp import EmailBackend

from amon.apps.notifications.mail.models import email_model

class AmonEmailBackend(EmailBackend):

    """
    A wrapper that manages the SMTP network connection.
    """
    def __init__(self, host=None, port=None, username=None, password=None,
                 use_tls=None, fail_silently=False, use_ssl=None, timeout=None,
                 ssl_keyfile=None, ssl_certfile=None,
                 **kwargs):
        super(AmonEmailBackend, self).__init__(fail_silently=fail_silently)
        email_settings = email_model.get_email_settings()

        self.host = email_settings.get('host')
        self.port = email_settings.get('port')
        self.username = email_settings.get('username', False)
        self.password = email_settings.get('password', False)
        self.use_tls = email_settings.get('use_tls', False)
        self.timeout = 10

        self.connection = None
        self._lock = threading.RLock()



    def open(self):
        if self.connection:
            return False
        try:

            self.connection = smtplib.SMTP(host=self.host, port=self.port,
                     local_hostname=DNS_NAME.get_fqdn(), timeout=self.timeout)

            if self.use_tls:
                self.connection.ehlo()
                self.connection.starttls()
                self.connection.ehlo()

            if self.username and self.password:
                self.connection.login(self.username, self.password)

            return True
        except:
            if not self.fail_silently:
                raise

    def close(self):
        """Closes the connection to the email server."""
        if self.connection is None:
            return
        try:
            try:
                self.connection.quit()
            except (ssl.SSLError, smtplib.SMTPServerDisconnected):
                # This happens when calling quit() on a TLS connection
                # sometimes, or when the connection was already disconnected
                # by the server.
                self.connection.close()
            except smtplib.SMTPException:
                if self.fail_silently:
                    return
                raise
        finally:
            self.connection = None


    def send_messages(self, email_messages):
        """
        Sends one or more EmailMessage objects and returns the number of email
        messages sent.
        """
        if not email_messages:
            return
        with self._lock:
            new_conn_created = self.open()
            if not self.connection:
                # We failed silently on open().
                # Trying to send would be pointless.
                return
            num_sent = 0
            for message in email_messages:
                sent = self._send(message)
                if sent:
                    num_sent += 1
            if new_conn_created:
                self.close()
        return num_sent

    def _send(self, email_message):

        """A helper method that does the actual sending."""

        if not email_message.recipients:
            return False
        # from_email = sanitize_address(email_message.from_email, email_message.encoding)
        # recipients = [sanitize_address(addr, email_message.encoding)
        #               for addr in email_message.recipients()]

        from_email = email_message.sender
        recipients = email_message.recipients
        message = email_message.as_string()


        try:
            self.connection.sendmail(from_email, recipients, message)
        except smtplib.SMTPException:
            if not self.fail_silently:
                raise
            return False
        return True
