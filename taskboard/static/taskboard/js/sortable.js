(function($){
  $(document).ready(function(){
    setupOverlay = function(){
      var width = $('#taskboard_list').width();
      var height = $('#taskboard_list').height();
      var top = $('#taskboard_list').offset().top;
      var left = $('#taskboard_list').offset().left;
      $('#taskboard_list_overlay').css({
        position: 'absolute',
        width: width,
        height: height,
        top: top,
        left: left
      });
    };
    updateList = function(){
      setupOverlay();
      $('#taskboard_list_overlay').fadeIn();
      $('#taskboard_list').load('list-items/', function(){
        $('#taskboard_list_overlay').fadeOut();
      });
    }
    $('.sortable').on('moved', updateList);
    $('.sortable').on('pre-move', function(e, data){
      if (data.target.indexOf('iteration') == 0) {
        var newTarget;
        if (data.target == 'iteration_unscheduled') {
          if (data.direction == 'dn') {
            data.target = 'unscheduled';
          } else {
            data.target = 'last';
          }
        } else {
          if (data.direction == 'dn') {
            newTarget = $('#task_'+data.target).prev();
          } else {
            newTarget = $('#task_'+data.target).next();
          }
        }
        if (newTarget && newTarget.length > 0) {
          data.target = newTarget.attr('id').replace('task_', '');
        }
      }
    });
  });
})(jQuery);
