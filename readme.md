23f2004496@ds.study.iitm.ac.in


XS43bs02

docker build -t tdspoc .
docker tag tdspoc:latest 779846818044.dkr.ecr.ap-south-1.amazonaws.com/tdspoc:latest
docker push 779846818044.dkr.ecr.ap-south-1.amazonaws.com/tdspoc:latest