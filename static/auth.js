/* eslint-env browser */
/* global Vue */

(function() {
  new Vue({
    el : "#authentication",
    data : {
      username : "",
      password : "",
      register : "",
      errors : [],
    },
    methods : {
      errorWrapper : function(type, p) {
        var _this = this;
        var errors = this.errors.filter(function(e) {
          console.log(e.errorType);
          return e.errorType !== type;
        });
        this.errors = errors;
        return p.catch(function(e) {
          e = e.message || e.toString();
          e.errorType = type;
          _this.errors = errors.concat(e);
          throw e;
        });
      },
      onUserName : function() {
        this.errorWrapper("username", validateUsername(this.username));
      },
      onPassword : function() {
        this.errorWrapper("password", validatePassword(this.password));
      },
      onSubmit : function() {
        var errors = this.errors;
        var _this = this;
        this.errorWrapper("submit", Promise.resolve().then(function() {
          if(errors.length > 0) {
            return Promise.reject("Still have form errors");
          }
          return sendRequest(_this);
        }));
      },
    }
  });

  function validateUsername(username) {
    if(username.length < 5) {
      return Promise.reject("username length < 5");
    }
    return Promise.resolve();
  }
  function validatePassword(password) {
    if(password.length < 5) {
      return Promise.reject("password length < 5");
    }
    return Promise.resolve();
  }
  function sendRequest(data) {
    var headers = new Headers();
    headers.append("Content-Type", "applications/json");
    return fetch("/api/login", {
      method : "post",
      headers : headers,
      body : JSON.stringify({
        username : data.username,
        password : data.password,
        register : data.register
      })
    }).then(function(resp) {
      if(resp.status !== 200) throw resp.toString();
      window.location = "/";
    });
  }

})();
