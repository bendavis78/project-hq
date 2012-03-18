(function($){
  $(document).ready(function(){
    $(document).on('click', 'a.status-action', function(e){
      e.stopPropagation();
      var $this = $(this)
      var href = $this.attr('href');
      var status = $this.attr('rel');
      $.ajax(href, {
        type: 'POST',
        data: {'status': status},
        success: function(data){
          $this.trigger('statusChanged', [data]);
        },
        error: function(xhr, textStatus) {
          var msg = 'An unknown error has occurred';
          if (xhr.status >= 400 && xhr.status < 500) {
            msg = xhr.responseText;
          }
          $(document).trigger('taskAjaxError', [msg]);
        }
      });
      return false;
    });
  });

  $.fn.setupOverlay = function(){
    console.log('setting up overlay for ', this);
    var $this = $(this);
    var width = $this.outerWidth();
    var height = $this.outerHeight();
    var top = $this.offset().top;
    var left = $this.offset().left;
    $('#task_overlay').remove()
    var overlay = $('<div id="task_overlay"></div>');
    overlay.css({
      display: 'none',
      position: 'absolute',
      width: width,
      height: height,
      top: top,
      left: left
    });
    $('body').append(overlay);
  };
})(jQuery);
