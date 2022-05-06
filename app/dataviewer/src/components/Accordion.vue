<template>
  <div :id="`accordion_${id}`" :class="accordionClass">
    <h5 class="heading">
      <button
        type="button"
        :id="`accordion_toggle_${id}`"
        class="toggle"
        :aria-controls="`accordion_content_${id}`"
        :aria-expanded="visible"
        v-on:click="onclick"
      >
        <span class="toggle_label">
          <span class="title-count">{{ titleCount }}</span>
          {{ title }}
        </span>
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          :class="iconClass" 
          fill="none"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          stroke="currentColor"
          stroke-width="2"
        >
          <path 
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M9 5l7 7-7 7"
          />
        </svg>
      </button>
    </h5>
    <section
      :id="`accordion_content_${id}`"
      class="content"
      :aria-labelledby="`accordion_toggle_${id}`"
      role="region"
      v-show="visible"
    >
      <slot></slot>
    </section>
  </div>
</template>

<script>
export default {
  name: 'Accordion',
  props: {
    id: String,
    title: String,
    titleCount: Number
  },
  data () {
    return {
      visible: false
    }
  },
  methods: {
    onclick () {
      this.visible = !this.visible
    }
  },
  computed: {
    accordionClass () {
      return this.visible ? 'accordion visible' : 'accordion'
    },
    iconClass () {
      return this.visible ? 'toggle_icon rotated' : 'toggle_icon'
    }
  }
}
</script>

<style lang="scss">
.accordion {
  font-family: inherit;
  box-sizing: border-box;
  border-radius: 6px;

  button {
    border: none;
    position: relative;
    background: none;
    background-color: none;
    margin: 0;
    padding: 0;
    cursor: pointer;
    font-size: inherit;
    text-align: left;
    color: currentColor;
  }

  .heading {
    display: flex;
    justify-content: flex-start;
    align-items: center;
    margin: 0;
    padding: 16px 12px;
    background-color: #ffffff;

    .toggle {
      display: flex;
      justify-content: flex-start;
      align-items: center;
      width: 100%;

      $icon-size: 24px;
      .toggle_label {
        display: inline-block;
        width: calc(100% - $icon-size);
        word-break: break-word;
        font-size: 11pt;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-left: 8px;
        
        .title-count {
          font-size: 14pt;
          font-weight: 600;
        }
      }

      .toggle_icon {
        width: $icon-size;
        height: $icon-size;
        transform: rotate(0);
        transform-origin: center;
        transition: transform 0.25s ease-in-out;

        &.rotated {
          transform: rotate(90deg);
        }
      }
    }
  }

  .content {
    margin: 0;
    padding: 12px;
  }
}
</style>
