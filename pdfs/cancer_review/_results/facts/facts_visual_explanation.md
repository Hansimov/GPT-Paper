**system**:
You are a helpful assistant. You can help me by answering my questions. You can also ask me questions.

--------------------

**user**:
以下是从几篇文章中摘录的一些片段，请你从中提取事实。
请注意，我正在撰写的论文章节主题是：Strategies for unraveling the “black-box” of AI-based Model-based explanation。
请着重关注 Visual explanation 方法的进展，并且我想阐述 Backpropagation-based approaches 和 Perturbation-based approaches 这两方面的现有工作。当然，你也可以从文本中提取出其他同level的方面的工作。
请你不要自己发挥，只针对我给出的文本，提取出事实。并且以markdown的格式输出。你的回复应当是英文。
你给出事实的格式应当是：谁在什么文章中提出了什么理论、做出了什么工作。你需要紧紧围绕章节的主题。

下面是论文 Explainable artificial intelligence (XAI) in deep learning-based medical image analysis 中的几个片段：
```
3.1. Visual explanation
Visual explanation, also called saliency mapping, is the most
common form of XAI in medical image analysis (Fig. 2). Saliency
maps show the important parts of an image for a decision.
Most saliency mapping techniques use backpropagation-based approaches, but some use perturbation-based or multiple instance
learning-based approaches. These approaches will be discussed below. An overview of papers using saliency maps in medical imaging is shown in Table 2.
```

```
3.1.1. Backpropagation-based approaches
(Guided) backpropagation and deconvolution: Some of the earliest techniques to create saliency maps highlighted pixels that
had the highest impact on the analysis output. Examples included
visualization of partial derivatives of the output on pixel level
(Simonyan et al., 2013), deconvolution (Zeiler and Fergus, 2014),
and guided backpropagation (Springenberg et al., 2014). These
techniques provided local, model-specific (only for CNNs), post hoc
explanation. These techniques have been used in medical image
analysis. For example, de Vos et al. (2019) estimated the amount
of coronary artery calcium per cardiac or chest computed tomography (CT) image slice, and used deconvolution to visualize from
where in the slice the decision was based on.
Class activation mapping (CAM): Zhou et al. (2016) introduced
Class Activation Mapping (CAM). They replaced the fully connected layers at the end of a CNN by global average pooling
on the last convolutional feature maps. The class activation map
was a weighted linear sum of presence of visual patterns (captured by the filters) at different spatial locations. This technique
provided local, model-specific, post hoc explanation. Several researchers used this technique in medical imaging (Table 2).
CAMs have also been used in medical image analysis in ensembles of CNNs. For example, Jiang et al. (2019) constructed
an ensemble of Inception-V3, ResNet-152, and Inception-ResNetV2 to distinguish fundus images of healthy subjects or patients
with mild diabetic retinopathy from those with moderate or severe diabetic retinopathy; and provided a weighted combination
of the resulting CAMs for localization of diabetic retinopathy.
Lee et al. (2019b) constructed CAMs of the output of an ensemble of four CNNs: VGG-16, ResNet-50, Inception-V3, and InceptionResNet-V2, for the detection of acute intracranial hemorrhage.
Since medical images often contain information at multiple scales, multi-scale CAMs have also been proposed
Liao et al. (2019) concatenated feature maps at three scales which
were subsequently provided as input for the global average pooling. The provided activation maps showed higher resolution than
single-scale maps, and were better at identifying small structures
on fundus images of the retina. Shinde et al. (2019a) concatenated
the feature maps of each layer before max-pooling and also gave
those as input to a global average pooling layer. Their ‘High
Resolution’ CAMs provided accurate localizations of brain tumors
on MRI. García-Peraza-Herrera et al. (2020) proposed extracting
CAMs at multiple resolutions. They showed that the CAMs at high
resolution were accurate in highlighting interpapillary capillary
loop patterns in endoscopy images, which were relatively small
compared to the entire image.
Gradient-weighted class activation mapping (Grad-CAM):
Selvaraju et al. (2017) introduced Gradient-weighted Class Activation Mapping (Grad-CAM), which is a generalization of CAM.
Grad-CAM can work with any type of CNN to produce post hoc
local explanation, whereas CAM specifically needs global average pooling. The authors also introduced guided Grad-CAM, an
element-wise multiplication between guided backpropagation and
Grad-CAM. Grad-CAM and Guided Grad-CAM have been used in
medical image analysis. For example, Ji (2019) used Grad-CAM to
show on which areas of histology lymph node sections a classifier
based its decision of metastatic tissue; Kowsari et al. (2020) used
it to pinpoint small bowel enteropathies on histology; and
Windisch et al. (2020) used Grad-Cam to show which areas
of brain MRI made the classifier decide on the presence of a
tumor.
Layer-wise relevance propagation (LRP): Bach et al. (2015) introduced layer-wise relevance propagation (LRP). LRP uses the output of the neural network, e.g. a classification score between 0
and 1, and iteratively backpropagates this throughout the network.
In each iteration (i.e., each layer), LRP assigns a relevance score
to each of the input neurons from the previous layers. These distributed relevance scores must equal the total relevance score of
its source neuron, according to the conservation law.
LRP has been used in medical image analysis. For example,
Böhle et al. (2019) used LRP for identifying regions responsible
for Alzheimer’s disease from brain MR images. They compared the
saliency maps provided by LRP with those provided by guided
backpropagation, and found that LRP was more specific in identifying regions known for Alzheimer’s disease.
Deep SHapley Additive exPlanations (Deep SHAP): Lundberg and
Lee (2017) proposed a unified approach for explaining predictions by using SHapley Additive exPlanations (SHAP). This modelagnostic approach used Shapley values (Shapley, 2016), a concept
from game theory. Shapley values determine the marginal contribution of every feature to the model’s output individually. A downside of Shapley values is that they are resource-intensive to compute, since they require assessment of many permutations.
By combining DeepLIFT with Shapley values, Lundberg and
Lee (2017) proposed a fast method to approximate Shapley values
for CNNs called Deep SHAP. Deep SHAP has been used in medical image analysis. For example, van der Velden et al. (2020) used
a regression CNN to estimate the volumetric breast density from
breast MRI. Deep SHAP was used to explain which parts of the image had a positive contribution and a which parts a negative contribution to the density estimation.
Trainable attention: While many of the previously mentioned
techniques highlighted what regions of the image the network focuses on, i.e. to where the attention was directed,
Jetley et al. (2018) proposed a trainable attention mechanism. This
trainable attention method highlighted where and in what proportion the network payed attention to input images for classification,
and used this attention to further amplify relevant areas and suppress irrelevant areas.
In medical imaging, Schlemper et al. (2019) used trainable attention and introduced grid attention. The rationale behind this
was that most objects of interest in medical images are highly
localized. By using grid attention, the trainable attention captured the anatomical information in medical images. They demonstrated high performance for both segmentation and localization,
by adding the attention gates to a UNET (Ronneberger et al., 2015)
and a variant of VGG (Simonyan and Zisserman, 2014). The attention coefficients were used to explain on which areas of the image
the network focused.
```

```
3.1.2. Perturbation-based approaches
3.1.2.1. Occlusion sensitivity
Perturbation-based techniques perturb the input image to assess the importance of certain areas of that image for the task under consideration. Zeiler and Fergus (2014) used an occlusion sensitivity analysis to visualize which parts of the image were most
important for classification. For example, they showed that an image of a dog holding a tennis ball was correctly classified by the
dog’s breed, except if the face of the dog was occluded, which
yielded the incorrect classification ‘tennis ball’.
3.1.2.2. Local interpretable model-agnostic explanations (LIME)
Ribeiro et al. (2016) introduced Local Interpretable Modelagnostic Explanations (LIME). LIME provides local explanation by
replacing a complex model locally with simpler models, for example by approximating a CNN by a linear model. By perturbing the
input data, the output of the complex model changes. LIME uses
the simpler model to learn the mapping between the perturbed
input data and the change in output. The similarity of the perturbed input to the original input is used as a weight, to ensure
that explanations provided by the simple models with highly perturbed inputs have less effect on the final explanation. In images,
Ribeiro et al. (2016) implemented the perturbations using superpixelsxxxxxxxxxxx is inclluded in the hyperlink"?>Achanta et al.,
2012), rather than individual pixels, to show which regions were
important for explaining a classification.
LIME has been used by several researchers in medical image
analysis. For example, Malhi et al. (2019) used LIME to explain
which areas in gastral endoscopy images contained bloody regions.
3.1.2.3. Meaningful perturbation
Fong and Vedaldi (2017) introduced meaningful perturbation,
where they perturbed the input image to detect changes in the
predictions of a trained neural network. Rather than using perturbations such as occlusion sensitivity that block out parts of the
image, they suggested simulating naturalistic or plausible effects,
leading to more meaningful perturbations, and consequently to
more meaningful explanations. They opted for three types of local
perturbations, namely a constant value, noise, or blurring.
Uzunova et al. (2019) stated that the perturbations proposed by
Fong and Vedaldi (2017) were not suited for medical images. Replacing areas of a medical image with a constant value is implausible, and medical images naturally tend to be noisy and blurry.
They proposed to replace pathological regions with a healthy tissue equivalent using a variational autoencoder (VAE). They showed
that the perturbations by the VAE pinpoint pathological regions
in diverse imaging studies as optical coherence tomography images of the eye (pathology consisted of intraretinal fluid, subretinal
fluid, and pigment epithelium detachments), and MRI of the brain
(pathology consisted of stroke lesions). Furthermore, they showed
that using a VAE yielded better localization of pathology compared
with using simple blurring or constant-value perturbations.
Lenis et al. (2020) used similar reasoning as
Uzunova et al. (2019), and used inpainting to replace pathological
regions with healthy tissue equivalents. They showed that the
perturbations created by inpainting outperformed backpropagation
and Grad-CAM in pinpointing masses in breast mammography
and tuberculosis on chest X-rays, based on the Hausdorff distance
between thresholded heatmaps derived from the saliency maps
and the ground truth labels at pixel level.
3.1.2.4. Prediction difference analysis
Zintgraf et al. (2017) adapted prediction difference analysis
(Robnik-Šikonja and Kononenko, 2008) for generating saliency
maps. If each pixel in an image is considered a feature, prediction difference analysis assigns a relevance value to each pixel, by
measuring how the prediction changes if the pixel is considered
unknown. Zintgraf et al. (2017) expanded this by adding conditional sampling, which means that they only analyzed pixels that
are hard to predict by simply investigating neighboring pixels, and
by adding multivariable analysis, which means that they analyzed
patches of connected pixels instead of single pixels. They included
an analysis of brain MRI of patients with HIV versus healthy controls, yielding explanation of the classifier’s decision.
Seo et al. (2020) used prediction difference analysis in combination with superpixels (or supervoxels for 3D) on multiple scales.
These multiscale supervoxel-based saliency maps provided explanations that the authors described as visually pleasing since they
follow image edges. The saliency maps explained which regions
were informative for a classifier to distinguish between Alzheimer’s
disease patients and normal controls.
3.1.3. Multiple instance learning-based approaches
Multiple instance learning can be used for visualizing explanations. In multiple instance learning, training sets consist of bags
of instances (Dietterich et al., 1997). These bags are labeled, but
the instances are not. In medical image analysis, multiple instance
learning can for example be done using a patch-based approach:
An image represents the bag, and patches from that image represent the instances (Cheplygina et al., 2019).
Several researchers have used this approach to pinpoint which
instances in the bag are responsible for the classification. For example, Schwab et al. (2020) localized critical findings in chest
X-ray using such a patch-based approach. Each image patch received a prediction, and the predictions were overlaid on the image to visualize on which areas the classifier based its decision.
Araújo et al. (2020) used multiple instance learning to explain
which areas of a fundus photograph were important for diabetic
retinopathy. They assessed the severity of the disease using an ordinal scale with grades from 0 to 5. Using a patch-based approach,
they provided visual explanation maps for each diabetic retinopathy grade.
```

--------------------

**assistant**:
Here are the facts extracted from the provided text, focusing on visual explanation methods, specifically backpropagation-based approaches and perturbation-based approaches:

### Backpropagation-based approaches

1. Simonyan et al. (2013) proposed visualization of partial derivatives of the output on pixel level.
2. Zeiler and Fergus (2014) introduced deconvolution for creating saliency maps.
3. Springenberg et al. (2014) developed guided backpropagation for saliency maps.
4. Zhou et al. (2016) introduced Class Activation Mapping (CAM) for local, model-specific, post hoc explanation.
5. Jiang et al. (2019) used an ensemble of CNNs and provided a weighted combination of CAMs for localization of diabetic retinopathy.
6. Lee et al. (2019b) constructed CAMs of the output of an ensemble of four CNNs for the detection of acute intracranial hemorrhage.
7. Liao et al. (2019) proposed multi-scale CAMs for better identification of small structures on fundus images of the retina.
8. Shinde et al. (2019a) developed 'High Resolution' CAMs for accurate localization of brain tumors on MRI.
9. García-Peraza-Herrera et al. (2020) proposed extracting CAMs at multiple resolutions for highlighting interpapillary capillary loop patterns in endoscopy images.
10. Selvaraju et al. (2017) introduced Gradient-weighted Class Activation Mapping (Grad-CAM) as a generalization of CAM.
11. Bach et al. (2015) introduced layer-wise relevance propagation (LRP) for assigning relevance scores to input neurons.
12. Lundberg and Lee (2017) proposed Deep SHapley Additive exPlanations (Deep SHAP) for explaining predictions using Shapley values.
13. Jetley et al. (2018) proposed a trainable attention mechanism for highlighting where the network pays attention to input images.
14. Schlemper et al. (2019) used trainable attention and introduced grid attention for capturing anatomical information in medical images.

### Perturbation-based approaches

1. Zeiler and Fergus (2014) used occlusion sensitivity analysis to visualize important parts of the image for classification.
2. Ribeiro et al. (2016) introduced Local Interpretable Model-agnostic Explanations (LIME) for providing local explanation by replacing complex models locally with simpler models.
3. Fong and Vedaldi (2017) introduced meaningful perturbation for detecting changes in predictions of a trained neural network.
4. Uzunova et al. (2019) proposed replacing pathological regions with healthy tissue equivalent using a variational autoencoder (VAE) for more meaningful perturbations.
5. Lenis et al. (2020) used inpainting to replace pathological regions with healthy tissue equivalents for better localization of pathology.
6. Zintgraf et al. (2017) adapted prediction difference analysis for generating saliency maps by assigning relevance values to each pixel.

### Multiple instance learning-based approaches

1. Schwab et al. (2020) used a patch-based approach with multiple instance learning to localize critical findings in chest X-ray.
2. Araújo et al. (2020) used multiple instance learning to explain important areas of a fundus photograph for diabetic retinopathy assessment.