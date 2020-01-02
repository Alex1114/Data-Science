# Install DGL

## Install from pip
For CUDA builds, run one of the following commands and specify the CUDA version.
```
pip3 install dgl           # For CPU Build
pip3 install dgl-cu90      # For CUDA 9.0 Build
pip3 install dgl-cu92      # For CUDA 9.2 Build
pip3 install dgl-cu100     # For CUDA 10.0 Build
pip3 install dgl-cu101     # For CUDA 10.1 Build
```

# Training
```
python3 training.py
```
Then the predict will in result file and I will choose the best loss!









<!-- ## CUDA build
```
mkdir build
cd build
cmake -DUSE_CUDA=ON ..
make -j4
```
Finally, install the Python binding.
```
cd ../python
python3 setup.py install
``` -->