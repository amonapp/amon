(function($) {
/* Format 

 <tr id="row-{{ id }}"></tr>
 <div class="delete-row" id="delete-row-{{ id }}">
    <a data-rowid="{{ id }}" href="" class="button cancel">Cancel</a>
 </div>

*/

DeleteRowView = Backbone.View.extend({
      
    el: $(".data-rows"),
       
    events: {
      "click .delete_row": "delete_row",
      "click .cancel": "cancel_delete"
    },

    delete_row: function(event){
        event.preventDefault();

        row_id = $(event.currentTarget).data('rowid');         
        row = $(render_underscore_template("#row-{{ row_id }}", [row_id]))
        row_position = row.offset();

        delete_overlay = $(render_underscore_template("#delete-row-{{ row_id }}", [row_id]));

        $(delete_overlay).css('top', row_position.top)
        .css('left', row_position.left)
        .css('width', row.width())
        .css('height', row.height()).show();
    },

    cancel_delete: function(event) {
        event.preventDefault();
        row_id = $(event.currentTarget).data('rowid');
        delete_overlay = $(render_underscore_template("#delete-row-{{ row_id }}", [row_id]));
        
        $(delete_overlay).hide();

    }
    
  });
  
  
  window.DeleteRowView = new DeleteRowView;

})(jQuery);