Vue.component('spa-inbox', {
  template: `
  <v-app id="inbox">
  
  <v-navigation-drawer
      v-model="drawer.left"
      clipped
      fixed
      app
    >
    <v-list two-line>
      <v-list-tile>
        <v-list-tile-avatar>
          <v-icon>filter_1</v-icon>
        </v-list-tile-avatar>
        
        <v-list-tile-content>
              <v-list-tile-title>Folder 1</v-list-tile-title>
              <v-tooltip bottom>
                <v-list-tile-sub-title  slot="activator">{{ actions.one.target_path }}</v-list-tile-sub-title>
                <span>{{ actions.one.target_path }}</span>
              </v-tooltip>
            </v-list-tile-content>
            
        <v-list-tile-action>
          <v-menu offset-y>
            <v-btn slot="activator" dark icon>
              <v-icon color="grey lighten-1">search</v-icon>
            </v-btn>
            <v-list>
              <v-list-tile
                v-for="(item, index) in media.children"
                :key="index"
                @click="setActionTargetPath(actions.one, item.path)"
              >
              <v-list-tile-title>{{ item.path }}</v-list-tile-title>
            </v-list-tile>
          </v-list>
        </v-menu>
      </v-list-tile-action>
      </v-list-tile>
      <v-divider></v-divider>
      <v-list-tile>
      <v-list-tile-avatar>
        <v-icon>filter_2</v-icon>
      </v-list-tile-avatar>
      <v-list-tile-content>
            <v-list-tile-title>Folder 2</v-list-tile-title>
            <v-tooltip bottom>
            <v-list-tile-sub-title slot="activator">{{ actions.two.target_path }}</v-list-tile-sub-title>
            <span>{{ actions.two.target_path }}</span>
              </v-tooltip>
      </v-list-tile-content>
      <v-list-tile-action>
        <v-menu offset-y>
          <v-btn slot="activator" dark icon>
            <v-icon color="grey lighten-1">search</v-icon>
          </v-btn>
          <v-list>
            <v-list-tile
              v-for="(item, index) in media.children"
              :key="index"
              @click="setActionTargetPath(actions.two, item.path)"
            >
            <v-list-tile-title>{{ item.path }}</v-list-tile-title>
          </v-list-tile>
        </v-list>
      </v-menu>
      </v-list-tile-action>
    </v-list-tile>
    <v-container >
      <v-treeview      
      :active.sync="folders.active"
      :open="folders.open"
      :items="folders.items"
      activatable
      item-key="name"
      ><template slot="prepend" slot-scope="{ open }">
        <v-icon>
          {{ open ? 'folder_open' : 'folder' }}
        </v-icon><v-icon></v-icon>
        </template>
      </v-treeview>
    </v-container>
      
    </v-list>
    
  </v-navigation-drawer>

  <v-toolbar app clipped-left>
    <v-toolbar-side-icon @click.stop="drawer.left = !drawer.left"></v-toolbar-side-icon>
    <v-toolbar-title class="white--text">
      Inbox -- {{parseFloat(current_item + 1) + ' of ' + media.assets.length + ' -- ' + media.assets[current_item].name}}
    </v-toolbar-title>
    <v-spacer></v-spacer>
    <v-btn v-if="undo.show" icon @click="undoLastAction"><v-icon>undo</v-icon></v-btn>
    <v-btn icon @click="trashCurrentItem"><v-icon>delete</v-icon></v-btn>
    <v-btn icon @click="action('one', media.assets[current_item])"><v-icon>filter_1</v-icon></v-btn>
    <v-btn icon @click="action('two', media.assets[current_item])"><v-icon>filter_2</v-icon></v-btn>
  </v-toolbar>
  
  <v-content>

  <!-- LIGHTBOX -->
  <div v-bind:style="{'height': window.height - toolbarHeight + 'px'}">
    <v-layout
    justify-center
    align-center
    fill-height
    >
    <v-btn dark large absolute middle left fab @click="previousImage"><v-icon>chevron_left</v-icon></v-btn>
    <v-layout
    justify-center
    align-center
    >
      <img
      ref="picture"
      :src="media.assets[current_item].lightboxUrl"
      :width="lightbox.width"
      :height="lightbox.height"
      @load="setImageSize"
      class="elevation-24">
    </v-layout>
    <v-btn dark large absolute middle right fab @click="nextImage"><v-icon>chevron_right</v-icon></v-btn>
    </v-layout>
  </div>
    
  <!-- CONFIRMATION DIALOG -->
  <v-dialog v-model="confirm.dialog" :max-width="confirm.width" @keydown.esc="confirm_cancel">
    <v-card>
      <v-toolbar dark :color="confirm.color" dense flat>
        <v-toolbar-title class="white--text">{{ confirm.title }}</v-toolbar-title>
      </v-toolbar>
      <v-card-text v-show="!!confirm.message">{{ confirm.message }}</v-card-text>
      <v-card-actions class="pt-0">
        <v-spacer></v-spacer>
        <v-btn color="primary darken-1" flat="flat" @click.native="confirm_agree">Yes</v-btn>
        <v-btn color="grey" flat="flat" @click.native="confirm_cancel">Cancel</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <!-- LOADING DIALOG -->
  <v-dialog v-model="loading.dialog" persistent width="300">
    <v-card color="primary" dark>
      <v-card-text>Loading...
        <v-progress-linear indeterminate color="white" class="mb-0"></v-progress-linear>
      </v-card-text>
    </v-card>
  </v-dialog>
  </v-content>

  <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :multi-line="snackbar.mode === 'multi-line'"
      :timeout="false"
      :vertical="snackbar.mode === 'vertical'"
    >
      {{ snackbar.text }}
      <v-btn
        v-if="undo.show"
        dark
        flat
        @click="undoLastAction"
      >
        Undo
      </v-btn>
      <v-btn
        dark
        flat
        @click="snackbar.show = false"
      >
        Close
      </v-btn>
    </v-snackbar>

</v-app>
        `,
  props: [],
  data() {
    return {
      media: [],
      current_item: 0,
      actions: {
        one: {
          target_path: '<not selected>', type: 'move'
        },
        two: {
          target_path: '<not selected>', type: 'move'       
        }
      },
      confirm: {
        dialog: false, resolve: null, reject: null,
        message: null, title: null, color: 'primary',
        width: 290
      },
      drawer: {
        left: false
      },
      lightbox: {
        show: false,
        width: 0,
        height: 0
      },
      loading: {
        dialog: false
      },
      snackbar: {
        show: false,
        color: 'info',
        mode: '',
        timeout: false,
        text: 'Hello, I\'m a snackbar'
      },
      undo: {
        show: false,
        text: '',
        url: '',
        media: []
      },
      window: {
        width: 0, height: 0
      },
      folders: {
        active: [],
        open: [],
        tree: [],
        items: [
          {
            name: 'INBOX',
            browseUrl: "http://127.0.0.1:6500/browse?path=",
            children: []
          }
        ]
      }
    }
  },
  methods: {
    action: function(action_number, item) {
      var self = this
      var action = self.actions[action_number]
      if (action.type == 'move') {
        self.move(item, action)
      }
    },
    handleResize: function() {
      this.window.width = window.innerWidth;
      this.window.height = window.innerHeight;
      if (this.$refs.picture) {
        this.setImageSize()
      }
      
    },
    confirm_open: function(title, message, options) {
      this.confirm.dialog = true
      this.confirm.title = title
      this.confirm.message = message
      return new Promise((resolve, reject) => {
        this.resolve = resolve
        this.reject = reject
      })
    },
    confirm_cancel: function() {
      this.resolve(false)
      this.confirm.dialog = false
    },
    confirm_agree: function() {
      this.resolve(true)
      this.confirm.dialog = false
    },
    async fetchFolders(item) {
      return fetch('https://jsonplaceholder.typicode.com/users')
        .then(res => res.json())
        .then(function(json) {
          console.log(json)
          item.children.push(...json)
        })
        .catch(err => console.warn(err))
    },
    gotoFolder: function (url) {
      // Alias the component instance as `vm`, so that we
      // can access it inside the promise function
      var self = this
      console.log('gotoFolder: ' + url)
      // Fetch our array of posts from an API
      self.loading.dialog = true
      this.$nextTick(() => {
        axios.get(url)
        .then(function(response) {
          console.log(response)
          self.media = response.data
          self.media.assets = response.data.assets.sort(function(a, b) {
            if (a.createdDate < b.createdDate) {
              return 1
            }
            if (a.createdDate > b.createdDate) {
              return -1
            }
            return 0
          })
          self.media.children = response.data.children.sort(function(a, b) {
            if (a.name < b.name) {
              return 1
            }
            if (a.name > b.name) {
              return -1
            }
            return 0
          })
          self.loading.dialog = false
        })
        .catch(function (error) {
          console.log(error);
        });
      });
    },
    setImageSize: function () {
      var img_width = this.$refs.picture.naturalWidth
      var img_height = this.$refs.picture.naturalHeight
      var image_aspect = this.$refs.picture.naturalWidth / this.$refs.picture.naturalHeight
      var window_aspect = this.window.width / this.window.height

      // if window aspect < image aspect, start with width, work out height
      if (window_aspect > image_aspect) {
        this.lightbox.width = this.maxImageHeight() * img_width/img_height
        this.lightbox.height = this.maxImageHeight()
      } else {
        this.lightbox.width = this.maxImageWidth()
        this.lightbox.height = this.maxImageWidth() * img_height/img_width
      }
    
    },
    maxImageHeight: function() {
      switch (this.$vuetify.breakpoint.name) {
        // window.height - toolbar height - arbitrary number
        case 'xs': return this.window.height - 54 - 40
        case 'sm': return this.window.height - 48 - 20
        case 'md': return this.window.height - 54 - 60
        case 'lg': return this.window.height - 64 - 60
        case 'xl': return this.window.height - 64 - 60
      }
    },
    maxImageWidth: function() {
      switch (this.$vuetify.breakpoint.name) {
        // window.height - toolbar height - arbitrary number
        case 'xs': return this.window.width - 40
        case 'sm': return this.window.width - 20
        case 'md': return this.window.width - 60
        case 'lg': return this.window.width - 60
        case 'xl': return this.window.width- 60
      }
    },
    move: function(item, action) {
      var self = this

      if (action.target_path == '<not selected>') {
        this.snackbar.text = 'You need to select a folder first'
        this.showSnackbar()
      } else {
        move_url = item.moveUrl + '?src_path=' + item.path + '&dest_path=' + action.target_path
        console.log(move_url)
        axios.put(move_url).then(function(response) {
          if (response.status == 200) {
            console.log('Moved!')
            // set undo - URL and media data
            self.undo.url = item.moveUrl + '?src_path=' + action.target_path + '/' + item.name + '&dest_path=' + item.parentPath
            self.undo.media = JSON.parse(JSON.stringify(self.media));
            self.undo.text = 'File moved back again (' + self.media.assets[self.current_item].name + ')'
            // show message
            self.snackbar.text = 'Moved file (' + self.media.assets[self.current_item].name + ')'
            self.undo.show = true
            self.showSnackbar()
            // remove item from media.assets
            self.media.assets.splice(self.current_item, 1)
          }
        })
      }
    },
    nextImage: function() {
      console.log('nextImage')
      this.current_item = (this.current_item < this.media.assets.length - 1) ? this.current_item + 1 : this.current_item
      console.log(this.selectedFolder)
    },
    previousImage: function() {
      console.log('previousImage')
      this.current_item = (this.current_item > 0) ? this.current_item - 1 : 0
    },
    setActionTargetPath: function(action, path) {
      console.log(action, path)
      action.target_path = path
    },
    showSnackbar: function () {
      clearTimeout(this.snackbar.timeout)
      var self = this
      this.snackbar.timeout = setTimeout(function(){ self.snackbar.show = false; }, 6000);
      this.snackbar.show = true
    },
    trashCurrentItem: function() {
      var self = this
      // try trash
      var trash_url = this.media.assets[this.current_item].trashUrl
      axios.put(trash_url).then(function(response) {
        if (response.status == 200) {
          console.log('Trashed!')
          // set undo - URL and media data
          self.undo.url = trash_url + '&restore=true'
          self.undo.media = JSON.parse(JSON.stringify(self.media));
          self.undo.text = 'File restored (' + self.media.assets[self.current_item].name + ')'
          // show message
          self.snackbar.text = 'Trashed file (' + self.media.assets[self.current_item].name + ')'
          self.undo.show = true
          self.showSnackbar()
          // remove item from media.assets
          self.media.assets.splice(self.current_item, 1)
        }
      })
    },
    undoLastAction: function() {
      var self = this
      // try undoing
      axios.put(this.undo.url).then(function(response) {
        if (response.status == 200) {
          console.log('Undone!')
          // restore media
          self.media = JSON.parse(JSON.stringify(self.undo.media));
          // show message
          self.snackbar.text = self.undo.text
          self.undo.show = false
          self.showSnackbar()
        } else {
          // show message
          self.snackbar.text = 'Could not undo!'
          self.showSnackbar()
        }
      })
      .catch(function (error) {
        console.log(error);
      }); 
    }
  },
  created: function () {
    console.log('created')
    var self = this

    window.addEventListener('resize', this.handleResize)
    this.handleResize();

    window.addEventListener('keyup', function(event) {
      this.console.log(event.keyCode)
      switch(event.keyCode) {
        case 8: // delete
          self.trashCurrentItem() 
        case 37: // left arrow
          self.previousImage()
          break
        case 39: // right arrow
          self.nextImage()
          break 
        case 49: // 1
          self.action('one', self.media.assets[self.current_item])
          break
        case 50: // 2
          self.action('two', self.media.assets[self.current_item])
          break
        case 90: // z
          self.undoLastAction() 
          break
      }
    });
    this.gotoFolder(this.$api_endpoint)
  },
  mounted: function() {
    console.log('mounted')
  },
  destroyed: function() {
    window.removeEventListener('resize', this.handleResize)
  },
  computed: {
    toolbarHeight() {
      switch (this.$vuetify.breakpoint.name) {
        // toolbar height
        case 'xs': return 54
        case 'sm': return 48
        case 'md': return 54
        case 'lg': return 64
        case 'xl': return 64
      }
    },
    selectedFolder () {
      if (!this.folders.active.length) return undefined

      const name = this.folders.active[0]

      var item = this.folders.items.find(item => item.name === name)
      return item.name
    }

  },
  watch: {
    selectedFolder: function(newValue, oldValue) {
      //console.log(newValue)
      //console.log(this.fetchFolders(this.folders.items[0]))
    }
  }
})