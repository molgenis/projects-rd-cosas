<template>
  <a class="action-link" :href="href" :target="showExternalLinkIcon ? '_blank' : false">
    <slot></slot>
    <svg
      v-if="showExternalLinkIcon"
      xmlns="http://www.w3.org/2000/svg"
      class="link-icon"
      fill="none"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      stroke="currentColor"
      stroke-width="2"
    >
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
      />
    </svg>
  </a>
</template>

<script>
export default {
  name: 'ActionLink',
  props: {
    href: {
      type: String,
      required: false
    },
    showExternalLinkIcon: {
      type: Boolean,
      default: false
    }
  }
}
</script>

<style lang="scss">
.action-link {
  display: block;
  width: 100%;
  text-align: center;
  color: $blue-800;
  box-sizing: border-box;
  padding: 0.5em 1em;
  border: 1px solid $blue-800;
  background-color: $blue-050;
  border-radius: 6px;
  margin: auto;
  
  .link-icon {
    margin-left: 3px;
    margin-top: -2px;
  }
  
  &:hover, &:focus {
    outline: 1px solid;
  }
}
</style>
