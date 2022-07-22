<template>
  <div :class="`search__results ${hasError ? 'search__error' : ''}`" v-if="hasError">
    <div class="error__box" v-if="hasError">
      <p class="error__box__message">
        <strong>{{ label }}</strong>
        <code>{{ actionErrorMessage }}</code>
      </p>
    </div>
    <div class="loading__box" v-else-if="isPerformingAction && !actionWasSuccessful && !actionHasFailed">
      <p>Searching....</p>
    </div>
    <div class="results__box" v-else>
      <p>{{ actionSuccessMessage }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'search-results-box',
  props: {
    label: {
      type: String,
      required: true
    },
    isPerformingAction: {
      type: Boolean,
      required: true,
      default: false
    },
    actionWasSuccessful: {
      type: Boolean,
      required: true,
      default: false
    },
    actionHasFailed: {
      type: Boolean,
      required: true,
      default: false
    },
    actionErrorMessage: {
      type: String,
      required: false
    },
    actionSuccessMessage: {
      tyoe: String,
      required: false,
      default: 'Action was successful'
    }
  },
  computed: {
    hasError () {
      return !this.isPerformingAction && !this.actionWasSuccessful && this.actionHasFailed
    }
  }
}
</script>

<style lang="scss" scoped>
.search__results {
  margin-top: 16px;
  box-sizing: border-box;
  padding: 1em;
  border-radius: 6px;
  background-color: $gray-050;
  &.search__error {
    background-color: $red-050;
    color: $red-900;
  }
  
  .loading__box, .results__box {
    text-align: center;
  }
  
  .error__box {
    .error__box__message {
      white-space: pre-wrap;
      
      code {
        color: currentColor;
      }
    }
  }
}
</style>
