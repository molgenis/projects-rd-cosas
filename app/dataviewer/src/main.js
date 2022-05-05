import Vue from "vue";
import VueRouter from "vue-router";

import App from "./App";
import RecordView from "./components/RecordView";

Vue.use(VueRouter);

/** use vue router only to react to change url attributes */
const router = new VueRouter({
  routes: [
    {
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