**system**:
You are a helpful assistant. You can help me by answering my questions. You can also ask me questions.

--------------------

**user**:
以下是从几篇文章中摘录的一些片段，请你从中提取事实。
请注意，我正在撰写的论文章节主题是：Strategies for unraveling the “black-box” of AI-based Model-based explanation，并且着重关注 Example-based explanation 方法的进展，并且我想阐述 Triplet network 和 Prototypes 这两方面的现有工作。当然，你也可以从文本中提取出其他同level的方面的工作。
请你不要自己发挥，只针对我给出的文本，提取出事实。并且以markdown的格式输出。你的回复应当是英文。
你给出事实的格式应当是：谁在什么文章中提出了什么理论、做出了什么工作。你需要紧紧围绕章节的主题。

下面是论文 Explainable artificial intelligence (XAI) in deep learning-based medical image analysis 中的几个片段：

```
3.3. Example-based explanation
Example-based explanation is an XAI technique that provides
examples relating to the data point that is currently being analyzed. This can be useful when trying to explain why a neural network came to a decision, and is related to how humans reason. For
example, when a pathologist examines a biopsy of a patient that
shows similarity with an earlier patient examined by the pathologist, the clinical decision may be enhanced by knowing the assessment of that earlier biopsy.
Example-based explanation often optimizes the hidden layers
deep in the neural network (i.e., the latent space) in such a way
that similar points are close to each other in this latent space,
while dissimilar points are further away in the latent space.
An overview of papers using example-based explanation in
medical imaging is shown in Table 4.
```

```
3.3.1. Triplet network
Several papers provided example-based explanation using a
triplet network (Hoffer and Ailon, 2015). A triplet network consists
of three identical networks with shared parameters. By feeding
these networks three input samples, the network calculates two
values consisting of the L2 distances between the representations
in the latent space (i.e., embedded representations) of these input
samples. This allows learning of useful representations by unsupervised comparison of samples. When analyzing a data point, inspection of neighbors in this embedded representation will provide
examples of data points that are similar to the data point that is
being analyzed, which can provide explanation why the network
came to its output.
Peng et al. (2019) used example-based explanation in colorectal
cancer histology. They first trained a CNN using a triplet loss, hashing, and k hard-negatives to learn an embedding that preserves
similarity. In testing, a coarse-to-fine search yielded the 10 nearest examples from a testing database related to the input image.
This provided explanation on which images similar to the image
that was being analyzed the network based a decision.
Yan et al. (2018) utilized a radiological picture archiving and
communication systems (PACS) to extract 32000 clinically relevant
lesions from the entire body. To learn relevant lesion embeddings,
they trained a triplet network with three supervision cues: lesion
size, lesion anatomical location (e.g. lung, liver, or kidney), and
relative coordinate of the lesion in the body. These embeddings
showed good separation based on anatomical location (e.g., liver
lesions were separated from lung lesions), and could accurately retrieve example-based explanation from a test set.
Codella et al. (2018) also used a triplet loss but combined it
with global average pooling, the technique used in CAM. Consequently, they could not only extract example-based explanation, but they also provided query activation maps and search result activation maps. In other words, a visual explanation showed
which region of the input image the network used to generate the
example-based explanation. They demonstrated this technique in
dermatology images of melanoma.
```

```
3.3.2. Influence functions
Wei Koh and Liang (2017) proposed to use influence functions
to explain on which inputs from a training set a decision was
based. They did so by investigating what would happen in case
an input from the training set would not be available or would
be changed. Since it is expensive to assess this by perturbation,
they provided an efficient approximation using influence functions
(Cook and Weisberg, 1980). This implementation of influence functions is related to SHAP in the sense that they both allow efficient
computation of feature importance.
Wang et al. (2019) used influence functions to explain which
classifications of liver lesions on multiphase MRI were associ-
ated with which radiological characteristics. This global explanation provided insight into the neural network’s behavior. For example, the class ‘benign cyst’ was most often associated with the
radiological finding ‘thin-walled mass’. Since the network did not
only output the class label but also the corresponding radiological characteristics, this explanation could enhance user trust in the
output of the network
```

```
3.3.3. Prototypes
Chen et al. 2019 proposed to use typical examples as explanation (i.e., prototypes), which they described as ‘this-looks-likethat’. The method reflected case-based reasoning that humans perform. For example, when a person explains why a picture contains
a car, they can internally reason that this is a car because it looks
like a car they have seen before. A prototype layer was added to
the neural network, which grouped training inputs according to
their classes in the latent space. A prototype was picked for each
class, consisting of a typical example of that class. During testing,
the method utilized parts of the test image that resembled these
trained prototypes. The output was a weighted combination of the
similarities to these prototypes. Hence, the explanation was an actual computation of the neural network, not a post hoc approximation.
Uehara et al. (2019) used prototypes to explain why a neural
network classified patches of histology images as cancer or as notcancer. The network was able to identify on which parts of the image it based its decision, and to what extent these parts of the image were similar to prototypical examples learned from the training set.
```

```
3.3.4. Examples from the latent space
Sarhan et al. (2019) proposed learning disentangled representations of the latent space using a residual adversarial VAE with
a total correlation constraint. This adversarial VAE enhanced the
fidelity of the reconstruction and provided more detailed descriptions of underlying generative characteristics of the data. When analyzing reconstructions by traversing through the latent space, they
showed that their method yielded reconstructions that were more
true to human-interpretable concepts such as lesion size, lesion eccentricity, and skin color compared with a regular VAE.
Biffi et al. (2020) provided a framework for explainable anatomical shape analysis using a ladder VAE (Sønderby et al., 2016). They
coupled this ladder VAE with a multi-layered perceptron, enabling
the network to train end-to-end for classification tasks. By doing
this, the highest level of the latent space was enforced to be lowdimensional (2D or 3D), which meant that these learned latent
spaces could be directly visualized without the need of further dimensionality reduction after training. They provided dataset-level
explanation using these low-dimensional latent spaces to visualize differences in shape for hypertrophic cardiomyopathy versus
healthy controls on cardiac MRI, and for Alzheimer’s disease versus healthy controls on brain MRI by visualizing the shape of the
hippocampus.
Silva et al. (2018) proposed example-based explanation that
showed similar and dissimilar cases foraesthetic results of breast
surgery on photos, and for skin images on dermoscopy. They identified these examples using a nearest neighbor search in latent
space: The nearest neighbor of the same class was considered the
most similar case, and the nearest neighbor of the other class
was considered the most dissimilar case. Their explanation also included rule extraction from meta-features (e.g. the color of a skin
lesion or the visibility of scars). They proposed three criteria to
measure the validity of the rule-extracted explanation, namely: (1)
completeness, i.e. the explanation should be general enough to be
applied to more than one observation; (2) correctness, i.e. if the
explanation itself was considered a model, it should correctly identify which class it belongs to; and (3) compactness, i.e. the explanation should be succinct.
In later work, Silva et al. (2020) combined example-based explanation with saliency mapping. First, they trained a baseline CNN
to classify chest X-rays into pleural effusion versus non-pleural effusion. After that, the CNN was fine-tuned on saliency maps. In
testing, a nearest neighbor search between the latent space of the
test image and a curated ‘catalogue’ set of images was performed.
Adding the saliency map yielded more consistent examples than
extracting examples without the saliency map (i.e., the baseline
CNN).
Sabour et al. (2017) showed that by replacing the scalar feature
maps from convolution neural networks by vectorized representations (i.e., capsules), they were able to encode high-level features
of images. Capsules were basically subcollections of neurons in a
layer. These were linked to subcollections of neurons in subsequent
layers, forming a capsule network. This capsule network was optimized using dynamic routing. In short, higher level capsules were
activated if their corresponding lower-level capsules are active.
This correspondence was described by routing coefficients, which
summed to one for each capsule. The coefficients were iteratively
(i.e., dynamically) updated when the capsule network received new
input data. For the MNIST digits dataset, Sabour et al. (2017) found
that these capsules learn human-interpretable features such as
scale, thickness, and skew.
LaLonde et al. (2020) used capsules for lung cancer diagnosis,
while also predicting visual attributes such as sphericity, lobulation, and texture. Since these visual attributes were not necessarily mutually exclusive, as was the case in MNIST (a digit cannot
be a two and a nine at the same time), they adapted the dynamic routing algorithm accordingly. Specifically, the routing coefficients did not have to sum to one in their implementation.
LaLonde et al. (2020) showed that their implementation was indeed able to predict these visual attributes as well as lung nodule
malignancy.
```

--------------------

**assistant**:
Based on the provided text, here are the extracted facts in the requested format:

1. In the paper "Explainable artificial intelligence (XAI) in deep learning-based medical image analysis," the authors discuss example-based explanation as an XAI technique that provides examples relating to the data point being analyzed.

2. Hoffer and Ailon (2015) introduced the concept of a triplet network, which consists of three identical networks with shared parameters. Peng et al. (2019) used example-based explanation with a triplet network in colorectal cancer histology, while Yan et al. (2018) utilized a triplet network to extract 32,000 clinically relevant lesions from the entire body. Codella et al. (2018) combined a triplet loss with global average pooling to provide example-based explanation and visual explanations in dermatology images of melanoma.

3. Wei Koh and Liang (2017) proposed using influence functions to explain which inputs from a training set a decision was based on. Wang et al. (2019) used influence functions to explain classifications of liver lesions on multiphase MRI and their association with radiological characteristics.

4. Chen et al. (2019) proposed using typical examples as explanation (i.e., prototypes) in a method called "this-looks-like-that." Uehara et al. (2019) used prototypes to explain why a neural network classified patches of histology images as cancer or not-cancer.

These facts are centered around the topic of "Strategies for unraveling the 'black-box' of AI-based Model-based explanation" and focus on the progress of example-based explanation methods, specifically in the areas of triplet networks and prototypes.

--------------------

**user**:
很棒，这就是我想要的！那么你能否将你上述的文本润色一下，并且用 triplet network、influence functions、prototypes 将其分组组织好，同时将不同人的工作放在新的行。

--------------------

**assistant**:
Certainly! Here's the revised text with the requested organization and formatting:

**Triplet Network**
- Hoffer and Ailon (2015) introduced the concept of a triplet network, consisting of three identical networks with shared parameters.
  - Peng et al. (2019) applied a triplet network for example-based explanation in colorectal cancer histology.
  - Yan et al. (2018) utilized a triplet network to extract 32,000 clinically relevant lesions from the entire body.
  - Codella et al. (2018) combined a triplet loss with global average pooling to provide example-based explanation and visual explanations in dermatology images of melanoma.

**Influence Functions**
- Wei Koh and Liang (2017) proposed using influence functions to explain which inputs from a training set a decision was based on.
  - Wang et al. (2019) applied influence functions to explain classifications of liver lesions on multiphase MRI and their association with radiological characteristics.

**Prototypes**
- Chen et al. (2019) proposed using typical examples as explanation (i.e., prototypes) in a method called "this-looks-like-that."
  - Uehara et al. (2019) used prototypes to explain why a neural network classified patches of histology images as cancer or not-cancer.

The revised text is now organized into groups based on the methods (triplet network, influence functions, and prototypes), with each author's work presented on a new line.