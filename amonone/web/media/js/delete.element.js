(function($) {
/* Format 

 <div id="element-{{ id }}"></div>
 <a href="#" data-id="{{ id }}" class='delete_element'></a>	
 <div class="delete-element" id="delete-element-{{ id }}">
	<a data-id="{{ id }}" href="" class="button cancel">Cancel</a>
 </div>

*/
DeleteElementView = Backbone.View.extend({
	  
	el: $(".data-rows"),
	   
	events: {
	  "click .delete_element": "delete_element",
	  "click .cancel": "cancel_delete"
	},

	delete_element: function(event){
	    event.preventDefault();

		id = $(event.currentTarget).data('id');

		element = $(_.template("#element-{{ id }}", [ id ]))
		element_position = element.offset();

		delete_overlay = $(_.template("#delete-element-{{ id }}", [ id ]));
				
		$(delete_overlay).css('top', element_position.top)
		.css('left', element_position.left)
		.css('width', element.width())
		.css('height', element.height()).show();
	},

	cancel_delete: function(event) {
		event.preventDefault();
		id = $(event.currentTarget).data('id');
		delete_overlay = $(_.template("#delete-element-{{ id }}", [ id ]));
		
		$(delete_overlay).hide();

	}
	
  });
  
  
  window.DeleteElementView = new DeleteElementView;

})(jQuery);