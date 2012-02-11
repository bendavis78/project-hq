(function($){
  $(document).ready(function(){
    var setParam = function(key, value) {
      var params = $.deparam.querystring()
      if (value == '') {
        delete params[key];
      } else {
        params[key] = value;
      }
      if (key == 'client' && value == '') {
        delete params['project'];
      }
      if (Object.keys(params).length > 0) {
        document.location.href = '?'+$.param(params)
      } else {
        document.location.href = '.';
      }
    }
    $('select.filter').change(function(){
      setParam(this.name, this.value);
    });
    $('#tickets_list tbody').sortable({
      'axis': 'y',
      'cursor': 'move',
      'update': function(event, ui) {
        var target;
        // target depends on which direction we're moving
        if (ui.originalPosition.top < ui.position.top) {
          target = ui.item.prev(); //dn
        } else {
          target = ui.item.next(); //up
        }
        var pk = ui.item.attr('id').replace('ticket_','');
        var target = target.attr('id').replace('ticket_','');
        var success;
        $.ajax(pk+'/move/'+target+'/', {
          async: false,
          error: function() {
            success = false;
          },
          success: function() {
            success = true;
          },
        });
        if (success == false) {
          return false;
        } else {
          // update zebra striping
          $('#tickets_list tbody tr:even').not('.ui-*').removeClass('even').addClass('odd');
          $('#tickets_list tbody tr:odd').not('.ui-*').removeClass('odd').addClass('even');
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
