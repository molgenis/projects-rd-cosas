<template>
  <ul :class="setClassNames">
    <slot></slot>
  </ul>
</template>

<script>
export default {
  name: 'unordered-lists',
  props: {
    noListStyle: {
      type: Boolean,
      default: false
    },
    stackList: {
      type: Boolean,
      default: true
    },
    showHorizontalSeparator: {
      type: Boolean,
      default: true
    },
    centerText: {
      type: Boolean,
      default: false
    },
    textToUppercase: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    setClassNames () {
      const baseClass = 'list'
      const styleClass = this.noListStyle ? 'list-no-style' : 'list-show-style'
      const orientationClass = this.stackList ? 'list-vertical' : 'list-horizontal'
      const separatorClass = !this.stackList & this.showHorizontalSeparator ? 'list-show-separator' : ''
      const textAlignmentClass = this.centerText ? 'list-text-center' : ''
      const textClass = this.textToUppercase ? 'list-text-to-upper' : ''
      return [baseClass, styleClass, orientationClass, textAlignmentClass, textClass, separatorClass].join(' ')
    }
  }
}
</script>

<style lang="scss">
.list {
  display: flex;
  justify-content: flex-start;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 0;
  padding: 0;
  margin: 0;
  color: currentColor;
  
  li {
    a {
      color: currentColor;
    }
  }
  
  &.list-text-to-upper {
    li {
      a {
        text-transform: uppercase;
        font-size: 11pt;
        letter-spacing: 0.08em;
      }
    }
  }
  
  &.list-text-center {
    justify-content: center;
  }
  
  &.list-no-style {
    list-style: none;
  }
  
  &.list-show-style {
    list-style: inherit;
  }
  
  &.list-vertical {
    flex-direction: column;
    gap: 0.2em;
  }
  
  &.list-horizontal {
    gap: 1em;
    flex-direction: row;
  }
  &.list-show-separator {
    li {
      position: relative;
      &::after {
        content: '';
        display: inline-block;
        margin-left: 0.85em;
        background-color: currentColor;
        border-radius: 50%;
        
        $size: 9px;
        width: $size;
        height: $size;
      }
      
      &:last-child {
        &::after {
          display: none;
        }
      }
    }
  }
}
</style>
