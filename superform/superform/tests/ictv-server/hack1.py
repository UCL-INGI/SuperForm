

class Hack(ICTVAuthPage):
    def GET(self, channel_id):
        if channel_id == '1':
            p = Plugin.get(1)
            p.set(activated='yes')
            l = self.plugin_manager.instantiate_plugin(self.app, p)
            plugin_dirs = self.plugin_manager.list_plugins()
            plugins = Plugin.update_plugins(plugin_dirs)
        chan = PluginChannel.get(channel_id)
        self.plugin_manager.add_mapping(self.app, chan)

