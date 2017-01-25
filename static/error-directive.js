/* global Vue */

(function() {
  Vue.component("error-message", {
    render : function(createElement) {
      return createElement(
        "div",   // tag name
        { style : "background-color: #FDD;" },
        this.$slots.default // array of children
      );
    },
  });
})();
