pipeline {
    agent any
    tools {
    maven 'maven' //ou java
  } 
  stages {
      stage('Build') {
          steps {
          sh 'docker build -t python/python .' 
          sh 'docker run -t python/python' 
        }
      } 
 }
}
