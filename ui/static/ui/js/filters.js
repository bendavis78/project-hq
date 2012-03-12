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
    $('input[name=search]').keypress(function(e){
      if (e.keyCode == 13) {
        setParam('q', this.value || '__all__');
      }
    });
  });
})(jQuery);
