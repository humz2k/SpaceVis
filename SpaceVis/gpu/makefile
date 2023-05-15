main: kernels tester

tester:
	clang++ test.cpp -o test.o -I /Users/humzaqureshi/GitHub/SpaceVis/metal-cpp -framework Metal -framework Foundation -framework Cocoa -framework CoreGraphics -framework MetalKit -fno-objc-arc

kernels:
	xcrun -sdk macosx metal -Wno-unused-variable -c kernels/render.metal -o kernels/render.air
	xcrun -sdk macosx metallib kernels/render.air -o kernels.metallib