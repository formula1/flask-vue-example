var tap = require("tap");
var fetch = require("isomorphic-fetch");

function handleGetRoute(routeName, route) {
  route = typeof route !== "string" ? routeName : route;
  return tap.test(`${routeName} returns 200`, function() {
    return fetch(`http://127.0.0.1:5000/${route}`).then(function(resp) {
      if(resp.status !== 200) throw `Invalid status ${resp.status}`;
    });
  });
}

handleGetRoute("index", "");
handleGetRoute("hello");
handleGetRoute("static/auth.js");
handleGetRoute("static/error-directive.js");
handleGetRoute("login");
