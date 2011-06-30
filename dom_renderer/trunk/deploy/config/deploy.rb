set :use_sudo, false

# fix capistrano bug with try_sudo which uses run_method which is set based on use_sudo BEFORE use_sudo is set above
set :run_method, :run

set :stages, %w(dev3 dev3.beta mfs2.sat)

require 'capistrano/ext/multistage'

set :application, "dom_renderer"
set :user, "dom_renderer"
set :runner, "dom_renderer"

set :repository, "svn+ssh://#{user}@svn.flowgram.com/var/svn/flowgram/dom_renderer/trunk"

# fix capistrano bug with windows not prompting for password http://groups.google.com/group/capistrano/browse_thread/thread/13b029f75b61c09d
#default_run_options[:pty] = true

after "deploy:symlink", :my_start_all

task :my_start_all do
  sudo "/usr/bin/svc -u /service/#{stage}_#{application}_*/log"
  sudo "/usr/bin/svc -u /service/#{stage}_#{application}_*"
end

task :my_stop_all do
  sudo "/usr/bin/svc -d /service/#{stage}_#{application}_*"
  sudo "/usr/bin/svc -d /service/#{stage}_#{application}_*/log"
end

namespace :deploy do
  task :svnup do
    my_stop_all
    
    run "svn up #{latest_release}"
    run "cd #{latest_release} && ant -Ddeploy.stage=#{stage}"
    
    my_start_all
  end
  
  task :finalize_update, :except => { :no_release => true } do
    my_stop_all
    
    run "cd #{latest_release} && ant -Ddeploy.stage=#{stage}"
  end

  task :restart do
  end
  
  # stop default migrate and start which are called on deploy:cold which is N/A since this is not a rails//web app
  task :migrate do
  end

  task :start do
  end
end
