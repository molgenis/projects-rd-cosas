
<template>
  <fieldset :id="id" class="checkbox-group">
    <legend class="checkbox-group-title">
      {{ title }}
      <span v-if="caption" class="caption">{{ caption }}</span>
    </legend>
    <div class="checkbox-group-options">
      <div class="group-option" v-for="option in options" :key="option">
        <input 
          type="checkbox"
          :id="option"
          :name="id"
          class="checkbox"
          :value="option"
          v-model="checkedOptions"
        />
        <label :for="option" class="label">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="label-check"
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
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <span>{{ option }}</span>
        </label>
      </div>
    </div>
  </fieldset>
</template>

<script>
export default {
  name: "CheckboxGroup",
  props: {
    id: String,
    title: String,
    caption: String,
    options: Array,
  },
  data () {
    return {
      checkedOptions: []
    }
  }
};
</script>

<style lang="scss">
.checkbox-group {
  border: 0;
  padding: 0;
  margin: 0;
  box-sizing: border-box;

  .checkbox-group-title {
    display: block;
    font-size: 13pt;
    letter-spacing: 0.06em;
    font-weight: 600;

    .caption {
      display: block;
      font-size: 11pt;
      letter-spacing: 0.02em;
      color: #353535;
      font-weight: normal;
    }
  }

  .checkbox-group-options {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    gap: 8px;

    .group-option {
      position: relative;

      .checkbox {
        position: absolute;
        width: 1px;
        height: 1px;
        clip: rect(0, 0, 0, 0);
        clip: rect(0 0 0 0);
        overflow: hidden;
        white-space: nowrap;

        + .label {
          display: block;
          text-align: center;
          padding: 2px 0;
          width: 135px;
          background-color: #F0F4FF;
          border: #2665FC solid 1px;
          border-radius: 12px;
          color: #2665FC;
          cursor: pointer;

          .label-check {
            position: absolute;
            top: 6px;
            left: 6px;
            width: 18px;
            height: 18px;
            opacity: 0;
          }
        }

        &:checked {
          + .label {
            background-color: #2665FC;
            color: #F0F4FF;
            .label-check {
              opacity: 1;
            }
          }
        }
        &:focus,
        &:hover {
          + .label {
            outline: solid;
          }
        }
      }
    }
  }
}
</style>