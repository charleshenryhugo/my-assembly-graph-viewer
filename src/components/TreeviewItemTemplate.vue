<template>
  <v-menu
    :close-on-content-click="false"
    max-width="400"
    offset-x
  >
    <template v-slot:activator="{ on }">
      <span v-on="on">
        {{ item.name }}
      </span>
    </template>
    <v-card
      class="mx-auto"
      max-width="400"
    >
      <v-card-text
        style="word-break: break-all"
        class="font-weight-bold"
      >
        {{ item.name }}
      </v-card-text>  
    </v-card>
  </v-menu>
</template>

<script>
export default {
  name: 'TreeViewTemplate',
  components: {
  },
  props: {
    item: Object,
  },
}
</script>

<style scoped>
</style>