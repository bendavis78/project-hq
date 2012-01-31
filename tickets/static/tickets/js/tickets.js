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
        console.log('client is none');
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
  });
})(jQuery);
