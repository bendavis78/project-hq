(function($){
  $(document).ready(function(){
    var setParam = function(key, value) {
      var params = $.deparam.querystring()
      if (value == '') {
        delete params[key];
      } else {
        params[key] = value;
      }
      if (Object.keys(params).length > 0) {
        document.location.href = '?'+$.param(params)
      } else {
        document.location.href = '.';
      }
    }
    $('div.tools select').change(function(){
      setParam(this.name, this.value);
    });
  });
})(jQuery);
