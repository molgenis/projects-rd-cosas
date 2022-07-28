<template>
  <div class="info__card">
    <h3 class="card__title">{{ title }}</h3>
    <p class="card__text"> {{ text }}</p>
    <ActionLink
      v-if="href"
      class="card__link"
      :href="href"
    >
      {{ hrefLabel ? hrefLabel : href }}
    </ActionLink>
    <slot></slot>
  </div>
</template>

<script>
import ActionLink from './ActionLink'

export default {
  name: 'info-card',
  props: {
    title: {
      type: String,
      required: true
    },
    text: {
      type: String,
      required: true
    },
    href: {
      type: String
    },
    hrefLabel: {
      type: String
    }
  },
  components: {
    ActionLink
  }
}
</script>

<style lang="scss" scoped>
.info__card {
  box-sizing: border-box;
  padding: 1.25em;
  background-color: $gray-000;
  border-radius: 6px;
  
  .card__title {
    font-size: 11pt;
    text-transform: uppercase;
    font-weight: 700;
    letter-spacing: 2px;
  }
  .card__link {
    display: block;
    width: 100%;
  }
}
</style>
