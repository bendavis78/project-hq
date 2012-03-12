(function($){
  $(document).ready(function(){
    $('.sortable').sortable({
      'axis': 'y',
      'cursor': 'move',
      'update': function(event, ui) {
        var target;
        var direction;
        // target depends on which direction we're moving
        if (ui.originalPosition.top < ui.position.top) {
          direction = 'dn';
          target = ui.item.prev(); //dn
        } else {
          direction = 'up';
          target = ui.item.next(); //up
        }
        var rel = ui.item.parents('.sortable').attr('rel');
        var pk = ui.item.attr('id').replace(rel+'_','');
        var target = target.attr('id').replace(rel+'_','');
        var success;
        data = {pk: pk, target: target, direction: direction}
        $(ui.item).parents('.sortable').trigger('pre-move', data);
        console.log('post-trigger data:', data);
        $.ajax(pk+'/move/'+data.target+'/', {
          async: false,
          error: function() {
            success = false;
          },
          success: function() {
            success = true;
            $(ui.item).parents('.sortable').trigger('moved', data);
          },
        });
        if (success == false) {
          return false;
        } else {
          // update zebra striping
          $('.sortable .row:even').not('.ui-*').removeClass('even').addClass('odd');
          $('.sortable .row:odd').not('.ui-*').removeClass('odd').addClass('even');
          // flash effect
          var prevBgColor = ui.item.css('background-color');
          ui.item.stop().css(
            'background-color', '#FFFF9C'
          ).animate({ 'background-color': prevBgColor }, 1500, function(){
            // remove the style declaration
            $(this).css('background-color', ''); 
          });
        }
      }
    }).disableSelection();
  });
})(jQuery);
