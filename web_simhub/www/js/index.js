/**
 * @Author: Hu
 * @Date: 2022年7月2日
 **/
;!function(win){
  "use strict";
  var Resize = function(option){
    this.$DEFAULT_OPTION = {max:40,min:10,rate:30};
    this.$option = Object.assign({}, this.$DEFAULT_OPTION, option);
    this.$el = document.body.parentNode
  };
  Resize.prototype.on = function(){
    var othis = this
    this.onEvent = function(e){
      othis.onResizeEvent.call(othis, e)
    }
    if (window.addEventListener) {
      window.addEventListener('resize', this.onEvent);
    }else if(window.attachEvent){
      window.attachEvent('onresize', this.onEvent);
    }
    this.onResizeEvent();
  };

  Resize.prototype.off = function(){
    if (this.onEvent) {
      if (window.removeEventListener) {
        window.removeEventListener('resize', this.onEvent);
      }else if (window.deatachEvent) {
        window.deatachEvent('onresize', this.onEvent);
      }
    }
  };

  Resize.prototype.onResizeEvent = function(){
    var o = this.$option
    var size = window.screen.width / o.rate
    if (size > o.max) {
      size = o.max
    }else if (size < o.min) {
      size = o.min
    }
    this.$el.style.fontSize = size + 'px'
  };

  var jq = {
    forEach:function(array, each){
      if (array&&array.length > 0) {
        var i=0, length = array.length;
        for(;i<length;i++){
          each.call(array, array[i], i)
        }
      }
    },
    AJAX_DEFAULT:{
      method:'get',
      timeout: 30000,
      responseType:'text',
      onSuccess:function(){},
      onError:function(){}
    },
    hasValue:function(val){
      if (val === undefined || val === null || val === '') {
        return false
      }
      return true
    },
    toQueryString:function(obj){
      if (obj) {
        var keys = Object.keys(obj);
        if (keys.length > 0) {
          var val;
          return keys.reduce(function(result, k){
            val = obj[k];
            if (jq.hasValue(val)) {
              result += (`&${k}=${val}`);
            }
            return result;
          },'').substring(1);
        }
      }
    },
    //options: 选项值
    //url, method, params(Object类型，Query String), data(Object类型，请求主体)
    //responseType(请求类型)，headers(Object类型，请求头)
    //onTimeout超时回调，onSuccess请求成功回调，onError请求失败回调
    ajax:function(url, options){
      if (typeof url === 'object') {
        options = url;
        url = options.url;
      }
      options = Object.assign({},jq.AJAX_DEFAULT, options);
      var xhr = win.XMLHttpRequest ? new XMLHttpRequest() : new ActiveXObject("Microsoft.XMLHTTP");
      if (options.params) {
        var qs = jq.toQueryString(options.params);
        if (qs) {
          options.url += ('?'+qs);
        }
      }if (options.onTimeout) {
        xhr.ontimeout = options.onTimeout;
      }
      var method = options.method.toUpperCase()
      xhr.responseType = options.responseType;
      xhr.open(method, url, true);
      xhr.onreadystatechange = function(){
        if(xhr.readyState === 4 && xhr.status === 200){
          options.onSuccess(xhr.responseText)
        }else{
          options.onError(xhr.response)
        }
      };
      if (options.headers) {
        Object.assign.keys(options.headers).forEach(function(k){
          xhr.setRequestHeader(k, options.headers[k]);
        });
      }
      if (/POST|PUT|PATCH/.test(method)) {
        //string, plain object, ArrayBuffer, ArrayBufferView, URLSearchParams
        //浏览器专属：FormData, File, Blob
        //Node 专属： Stream
        xhr.send(options.data);
      }else{
        xhr.send(null);
      }
    },
    queryByTag(selector){
      return document.getElementsByTagName(selector);
    },
    queryById(selector){
      return document.getElementById(selector);
    }
  };

  var ELEM = {
    carrier:jq.queryById('carrier'),
    signal:jq.queryById('signal'),
    total:jq.queryById('total'),
    balance:jq.queryById('balance'),
    deviceId:jq.queryById('deviceId'),
    dialog:jq.queryById('dialog')
  };
  var ON_EVENT = {
    buttonClick(e){
      //按钮点击事件
      ELEM.carrier.innerHTML = e.target.dataset.text
    }
  };
  new Resize().on();
  var buttons = jq.queryByTag('button');
  jq.forEach(buttons, function(btn){
    if (btn.addEventListener) {
      btn.addEventListener('click', ON_EVENT.buttonClick);
    }else if(btn.attachEvent){
      btn.addEventListener('onclick',ON_EVENT.buttonClick);
    }
  });
  var options = {
  onSuccess:function(resp){
            var resp_json = JSON.parse(resp)
            ELEM.carrier.innerHTML = resp_json["carrier"]
            ELEM.signal.innerHTML = resp_json["signal"]
            ELEM.total.innerHTML = resp_json["total"]
            ELEM.balance.innerHTML = resp_json["balance"]
            ELEM.deviceId.innerHTML = resp_json["deviceId"]
            console.log(resp)
        }
  }
jq.ajax("http://192.168.1.1/sim-info",options)



}(window);


var wssocket = new WebSocket("ws://192.168.1.1/ws");
wssocket.onopen = function(e){
            console.log("ws:open:", e);

        }
wssocket.onmessage = function(event) {
            console.log("message received", event.data);
            var resp_json = JSON.parse(event.data)
            document.getElementById("total").innerHTML =  resp_json["used"]
            document.getElementById("balance").innerHTML = resp_json["balance"]
        }
wssocket.onclose = function (e) {
 console.warn("ws:close:", e);

}

wssocket.onerror = function (e) {
               console.error("ws:error:", e);
}
