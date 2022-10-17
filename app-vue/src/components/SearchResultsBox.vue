<template>
  <div :class="`search__results ${hasError ? 'search__error' : ''}`" v-if="hasError || hasAction || hasResult">
    <div class="error__box" v-if="hasError">
      <p class="error__box__message">
        <strong>{{ label }}</strong>
        <code>{{ actionErrorMessage }}</code>
      </p>
    </div>
    <LoadingBox v-else-if="hasAction" message="Searching for files" />
    <div class="results__box" v-else-if="hasResult">
      <p>Found <strong>{{ totalRecordsFound }}</strong> record{{ totalRecordsFound == 1 ? '' : 's' }}</p>
      <ActionLink :href="searchResultsUrl" :showExternalLinkIcon="true" v-if="totalRecordsFound > 0">
        View Results
      </ActionLink>
    </div>
  </div>
</template>

<script>
import LoadingBox from './Loading.vue'
import ActionLink from './ActionLink.vue'

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
    totalRecordsFound: {
      type: Number,
      required: false
    },
    searchResultsUrl: {
      type: String,
      required: false
    }
  },
  components: {
    LoadingBox,
    ActionLink
  },
  computed: {
    hasAction () {
      return this.isPerformingAction && !this.actionWasSuccessful && !this.actionHasFailed
    },
    hasError () {
      return !this.isPerformingAction && !this.actionWasSuccessful && this.actionHasFailed
    },
    hasResult () {
      return !this.isPerformingAction && this.actionWasSuccessful && !this.actionHasFailed
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
        display: block;
        color: currentColor;
      }
    }
  }
  
  .results__box {
    display: grid;
    grid-template-columns: 1.75fr 1.25fr;
    justify-content: center;
    align-items: center;
    
    p {
      margin: 0;
    }
    .action-link {
      background-color: $blue-800;
      color: $gray-050;
      padding: 4px 0;
    }
  }
  
}
</style>
