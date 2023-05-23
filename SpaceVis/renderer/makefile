main:
	g++-12 renderer.cpp -o renderer.dll --shared -fopenmp

gpu:
	fpc++ renderer_gpu.cpp -o renderer_gpu.dll --shared -t Metal

clean:
	rm renderer.dll
	rm *.o