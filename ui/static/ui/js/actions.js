(function($){
  $(document).ready(function(){
    var checkBoxes = $('div.module .col.selector input[type=checkbox]');
    window.doAction = function(action, action_value) {
      $('#action_form input[name=action]').val(action);
      if (action_value) {
        $('#action_form input[name=action_value]').val(action_value);
      }
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
    checkBoxes.change(toggleActionBar);
    $('#action_form input.select-all').change(function(){
      checkBoxes.each(function(){
        this.checked = True;
        toggleActionBar();
      });
    });
  });
})(jQuery);
