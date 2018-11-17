Vue.component('spa-albums', {
  template: `
<v-list two-line subheader>
    
  <!-- FOLDERS -->
  <v-subheader>Folders</v-subheader>
  <v-container fluid grid-list-md>
    <v-layout row wrap>      
      <v-flex v-if="data.parentUrl !== null" @click="gotoFolder(data.parentUrl)" d-flex xs12 sm6 md4 lg3>
        <v-card>
          <v-layout>
            <v-flex><v-card-title> 
            <div>
                <span>..</span>
              </div>
            </v-card-title></v-flex>            
            <v-card-actions>
            </v-card-actions>
          </v-layout>
        </v-card>
      </v-flex>
    </v-layout>
  </v-container>

  <v-container fluid grid-list-md>
    <v-layout row wrap>      
      <v-flex v-for="item in data.subFolders" @click="gotoFolder(item.url)" :key="item.path" d-flex xs12 sm6 md4 lg3>
        <v-card >
          <v-layout>
            <v-flex><v-card-title> 
              <div><span></span>{{ item.name }}</span></div>
            </v-card-title></v-flex>            
            <v-card-actions>
            </v-card-actions>
          </v-layout>
        </v-card>
      </v-flex>
    </v-layout>
  </v-container>

  <!-- IMAGES -->
  <v-subheader>Images</v-subheader>
  <v-container fluid grid-list-md>
    <v-layout row wrap>      
      <v-flex v-for="(item, i) in data.mediaFiles" :key="i" d-flex xs12 sm6 md4 lg3>
        <v-card ref="mediaFile">
          <v-img :src="item.contentUrl + '?w=400'" aspect-ratio="1.778"></v-img>            
          <v-card-title>
            <div>
              <span class="grey--text mb-0">{{ item.name }}</span>
              <span>{{ item.description }}</span>
            </div>
          </v-card-title>            
          <v-card-actions>
            <!--<v-rating
              v-model="item.exif['EXIF:Rating']"
              color="yellow darken-3"
              background-color="grey darken-1"
              empty-icon="$vuetify.icons.ratingFull"
              hover
            ></v-rating>-->
            <v-btn flat icon color="orange" @click="del(item)"><v-icon>delete</v-icon></v-btn>
            <!--<v-btn flat icon color="orange" @click="save(item)"><v-icon>save</v-icon></v-btn>-->
          </v-card-actions>
        </v-card>
      </v-flex>
    </v-layout>
  </v-container>

  <!-- LIGHTBOX DIALOG -->
  <v-dialog v-model="lightbox.dialog" fullscreen hide-overlay transition="fade-transition" dark>
    <v-card>
      <v-toolbar dark color="primary">
        <v-btn icon dark @click.native="lightbox.dialog = false">
          <v-icon>close</v-icon>
        </v-btn>
        <v-toolbar-title>Settings</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-toolbar-items>
          <v-btn dark flat @click.native="lightbox.dialog = false">Save</v-btn>
        </v-toolbar-items>
      </v-toolbar>
      <v-container align-center justify-center>
      <!--<v-img src="http://192.168.1.112:6500/mediafile/content/test.cr2"
      :max-width="window.width - 100"
      :max-height="window.height - 100"
      ></v-img>-->
      </v-container>
    </v-card>
  </v-dialog>

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
<v-dialog
      v-model="loading.dialog"
      persistent
      width="300"
    >
      <v-card
        color="primary"
        dark
      >
        <v-card-text>
          Loading...
          <v-progress-linear
            indeterminate
            color="white"
            class="mb-0"
          ></v-progress-linear>
        </v-card-text>
      </v-card>
    </v-dialog>

</v-list>
        `,
  props: [],
  data() {
    return {
      data: [],
      dialog: false,
      lightbox: {
        dialog: false
      },
      window: {
        width: 0,
        height: 0
      },
      confirm: {
        dialog: false,
        resolve: null,
        reject: null,
        message: null,
        title: null,
        color: 'primary',
        width: 290
      },
      loading: {
        dialog: false
      }
    }
  },
  methods: {
    gotoFolder: function (url) {
      // Alias the component instance as `vm`, so that we
      // can access it inside the promise function
      var self = this
      console.log('gotoFolder' + url)
      // Fetch our array of posts from an API
      /*fetch(url)
        .then(function (response) {
          return response.json()
        })
        .then(function (data) {
          self.data = data
          console.log(data)
        })*/
      this.loading.dialog = true
      axios.get(url)
      .then(function(response) {
        console.log(response)
        self.data = response.data
      })
      .catch(function (error) {
        console.log(error);
      });
      this.loading.dialog = false
    },
    handleResize: function() {
      this.window.width = window.innerWidth;
      this.window.height = window.innerHeight;
    },
    save: function(item) {
      axios.put(item.metadataUrl, item)
      .then(function (response) {
        console.log(response);
      })
      .catch(function (error) {
        console.log(error);
      });
    },
    del: function(item) {
      // Alias the component instance as `vm`, so that we
      // can access it inside the promise function
      let self = this
      // Open confirmation dialog
      this.confirm_open('Move to Trash', 'Are you sure?', { color: 'red' }).then(
        function(result) {
          if (result == true) {
            // Send delete request
            axios.delete(item.contentUrl)
            .then(function (response) {
              console.log(response);
              // If request successful, iterate through local mediaFiles and remove mediaFile
              if (response.data == true) {
                for (var i = 0; i < self.data.mediaFiles.length; i++) {
                  if (item.contentUrl == self.data.mediaFiles[i].contentUrl) {
                    self.data.mediaFiles.splice(i, 1)
                  }
                }
              }
            })
            .catch(function (error) {
              console.log(error);
            });
          }
        },
        function(err) {
            console.log(err); // Error: "It broke"
        });
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
    }
  },
  created: function () {
    console.log('created')
    this.gotoFolder(this.$api_endpoint)
    window.addEventListener('resize', this.handleResize)
    this.handleResize();
  },
  destroyed: function() {
    window.removeEventListener('resize', this.handleResize)
  }
})