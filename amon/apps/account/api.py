from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework import status

# from amon.apps.account.models import user_preferences_model


# class UserPreferencesView(APIView):


#     def post(self, request):
#         sidebar = request.data.get('sidebar','wide')

#         data = {'sidebar': sidebar}
#         user_preferences_model.save_preferences(user_id=request.user.id, data=data)


#         return Response(status=status.HTTP_200_OK)
