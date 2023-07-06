# dogs and cats image generation

putting this on hold. was adapting this vae implementation: https://towardsdatascience.com/variational-autoencoder-demystified-with-pytorch-implementation-3a06bee395ed
ran into issues trying to generate dogs and cats. tried perceptual loss, but that only mildly improved things.
was able to reproduce cifar-10 quality.

the dogs and cats images are hard to see when resolution is reduced enough to fit into gpu memory. so that could be an issue trying to generate images.

may revisit this. the solution might be to just use a better gpu and run closer to imagenet resolution. might try different types of VAEs or GANS
