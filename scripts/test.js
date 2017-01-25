/* eslint-env node */
var path = require("path");
var serverSetup = require("./server-setup");
var promiseSpawn = require("child-process-promise").spawn;
var WalkDir = require("walk");

serverSetup.ensure().catch(function() {
  return serverSetup.start();
}).then(function() {
  return new Promise(function(res) {
    var walker = WalkDir.walk(path.join(__dirname, "../tests"));

    walker.on("file", function(root, stats, next) {
      if(!/\.js$/.test(stats.name)) {
        return next();
      }
      var promise = promiseSpawn("node", [path.join(root, stats.name)]);

      var childProcess = promise.childProcess;

      childProcess.stdout.on("data", function(data) {
        process.stdout.write(data);
      });
      childProcess.stderr.on("data", function(data) {
        process.stderr.write(data);
      });

      promise.then(function() {
        next();
      }).catch(function() {
        next();
      });
    });

    walker.on("errors", function(root, nodeStatsArray, next) {
      next();
    });

    walker.on("end", function() {
      res();
    });
  });
}).then(function() {
  console.log("kill");
  process.exit();
}, function(e) {
  console.error(e);
  process.exit();
});
