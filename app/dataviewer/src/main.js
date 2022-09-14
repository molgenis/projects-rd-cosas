import Vue from "vue";
import VueRouter from "vue-router";

import App from "./App";
import RecordView from "./pages/RecordView";

Vue.use(VueRouter);

/** use vue router only to react to change url attributes */
const router = new VueRouter({
  routes: [
    {
      name: "recordView",
      path: "/",
      component: RecordView,
      props: true,
    }
  ],
});

new Vue({
  router,
  render: (h) => h(App),
}).$mount("#app");