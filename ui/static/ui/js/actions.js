(function($){
  $(document).ready(function(){
    var checkBoxes = $('div.module .col.selector input[type=checkbox]');
    function doAction(action) {
      $('#action_form').submit();
    }
    function toggleActionBar() {
      var numChecked = checkBoxes.filter(':checked').length
      if (numChecked > 0) {
        $('div.tools.filters').slideUp();
        $('div.tools.actions').slideDown();
      } else {
        $('div.tools.actions').slideUp();
        $('div.tools.filters').slideDown();
      }
    }
    $('#action_form input.select-all').change(function(){
      checkBoxes.each(function(){
        this.checked = True;
        toggleActionBar();
      });
    });
    checkBoxes.change(toggleActionBar)
  });
})(jQuery);
