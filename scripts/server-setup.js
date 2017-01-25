/* eslint-env node */
var child_process = require("child_process");
var fetch = require("isomorphic-fetch");
var path = require("path");

var __root = path.join(__dirname, "../");

module.exports.ensure = function() {
  return fetch("http://localhost:5000/test-init").then(function(resp) {
    if(resp.status !== 200) {
      throw "bad status: " + resp.status;
    }
    if(resp.string() !== __root) {
      throw "not our server";
    }
    return true;
  });
};

module.exports.start = function() {
  return new Promise(function(res, rej) {
    var resolved = false;
    var buffer = "";
    var test = new RegExp(`\s*${
      escapeRegExp("* Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)")
    }\s*`);
    var errorlistener, stderrlistener, stdoutlistener;
    var c = child_process.spawn("npm", ["run", "fresh-start"], {
      cwd : __root,
      stdio : ["ignore", "pipe", "pipe"]
    });

    function checkFinish(data) {
      if(resolved) return;
      buffer += data.toString("utf-8");
      var line = buffer.replace("\n", "");
      if(!test.test(line)) return;
      resolved = true;
      buffer = "";
      c.stdout.removeListener("data", stdoutlistener);
      c.stderr.removeListener("data", stderrlistener);
      c.removeListener("error", errorlistener);
      res();
    }

    c.stdout.on("data", stdoutlistener = checkFinish);
    c.stderr.on("data", stderrlistener = checkFinish);

    c.once("error", errorlistener = function(error) {
      rej(error);
    });

  });
};

function escapeRegExp(str) {
  return str.replace(/[\-\[\]\/\{\}\(\)\*\+\?\.\\\^\$\|]/g, "\\$&");
}
