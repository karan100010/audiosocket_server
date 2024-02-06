#write a dictionary that maps the paths of docker containers

prefix="http://192.168.56.1"

docker_paths={"trancribe hindi":prefix+":5000/convert",
"trancribe english":prefix+":5001/convert",
"translate hi":prefix+":"+5002+"/convert",
"language id":prefix+":5003/convert",
}