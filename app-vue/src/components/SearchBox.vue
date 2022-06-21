<template>
  <fieldset class="form__input input__search__container">
    <SearchInput
      :id="id"
      :label="label"
      :description="description"
    />
    <button :id="id + '-btn'" class="btn-search" @click="search">
      {{ btnLabel }}
    </button>
  </fieldset>
</template>

<script>
import SearchInput from './SearchInput.vue'

export default {
  name: 'search-box',
  props: {
    id: {
      type: String,
      required: true
    },
    label: {
      type: String,
      required: true
    },
    description: {
      type: String,
      required: false
    },
    btnLabel: {
      type: String,
      required: false,
      default: 'Search'
    },
    tableId: {
      type: String,
      required: true
    },
    columnName: {
      type: String,
      required: true
    }
  },
  components: {
    SearchInput
  },
  methods: {
    search (event) {
      event.preventDefault()
      const relativeUrl = '/menu/plugins/dataexplorer?entity=' + this.tableId
      const inputElement = this.$el.childNodes[0].childNodes[1]
      const value = inputElement.value
      const searchUrl = relativeUrl + '&filter=' + this.columnName + '==' + value
      // window.location.replace(searchUrl)
      console.log(searchUrl)
    }
  }
}
</script>

<style lang="scss">
.input__search__container {
  .input__label {
    display: block;
    
    .input__description {
      display: block;
      color: #3f454b;
    }
  }
}
</style>
