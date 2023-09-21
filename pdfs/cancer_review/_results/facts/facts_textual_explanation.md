**system**:
You are a helpful assistant. You can help me by answering my questions. You can also ask me questions.

--------------------

**user**:
以下是从文章 Explainable artificial intelligence (XAI) in deep learning-based medical image analysis 中摘录的一些片段，请你从中提取事实。
请注意，我正在撰写的论文章节主题是：Strategies for unraveling the “black-box” of AI-based Model-based explanation，并且着重关注 Textual Explanation 方法的进展，并且我想阐述 Image captioning 和 Image captioning with visual explanation 这两方面的现有工作。当然，你也可以从文本中提取出其他同level的方面的工作。
请你不要自己发挥，只针对我给出的文本，提取出事实。并且以markdown的格式输出。你的回复应当是英文。
你给出事实的格式应当是：谁在什么文章中提出了什么理论、做出了什么工作。你需要紧紧围绕章节的主题。
下面是论文片段：

```
3.2. Textual explanation
Textual explanation is a form of XAI that provides textual descriptions. Such descriptions include relatively simple characteristics (e.g. ‘spiculated mass’), up to entire medical reports. We will
describe three types of textual explanation: image captioning, image captioning with visual explanation, and testing with concept
attribution.
An overview of papers using textual explanation in medical
imaging is shown in Table 3.
```

```
3.2.1. Image captioning
Vinyals et al. (2015) provided textual explanation for images using an end-to-end image captioning framework. They coupled a
convolutional neural network for encoding of the image, with a recurrent neural network – specifically a long-short term memory
net (LSTM) (Hochreiter and Schmidhuber, 1997) – for textual encoding. They used human-generated sentences as ground truth for
training, and used the bilingual evaluation understudy (BLEU) metric for evaluation. The BLEU-metric describes the precision of word
N-grams, i.e. a sequence of N words, between generated and reference sentences (Papineni et al., 2002).
Singh et al. (2019) used an image captioning framework to
provide textual explanation for chest X-rays. They used wordembedding databases Global Vectors (GloVe) (Pennington et al.,
2014) and the radiology variant RadGloVe (Zhang et al., 2018) to
train the LSTM, and used the aforementioned BLEU metric as well
as variants METEOR, CIDER, and ROUGE (Banerjee and Lavie, 2005;
Lin, 2004; Vedantam et al., 2015). As expected, higher performance
was reached in the generated radiology report when both RadGloVe and GloVe were used instead of just GloVe.
```

```
3.2.2. Image captioning with visual explanation
Several researchers combined image captioning with visual explanation. Zhang et al. (2017a) introduced a framework that used
dual attention, both for text and for imaging. They used a similar
approach as with image captioning, i.e. an encoder for the image
and an LSTM for the text, but added dual attention. This facilitated high-level interactions between image and text predictions,
and yielded visual attention maps corresponding with textual explanation in Histology images.
Wang et al. 2018 used a similar approach, and showed in their
chest X-ray example that different parts of the textual explanation led to different areas of saliency mapping in the image. They
showed a saliency map of the chest with multiple regions corresponding to different radiological findings.
Lee et al. (2019a) showed image captioning with visual explanation for breast mammograms. They added a visual word constraint
loss to the text-generating LSTM, to ensure that the provided explanations follow the correct jargon of breast mammography reports. They showed that adding this loss aids in generating better
textual explanation. Furthermore, they linked the radiology reports
to visual saliency maps.
```

```
3.2.3. Testing with concept activation vectors (TCAV)
Concept attributions provide explanation corresponding to
high-level concepts that humans find easy to understand
(Kim et al., 2018). Using Testing with Concept Activation Vectors
(TCAV), Kim et al. (2018) presented human-friendly linear explanations of the internal state of neural networks, yielding global explanation of the networks in terms of human-understandable concepts. These concepts can be provided after training of the neural network as a post hoc analysis. The TCAV algorithm uses userdefined sets of examples of a concept and of random non-concept
examples. Such a concept might be ‘stripes’ to assess whether an
image contained a zebra, or ‘spiculated mass’ to assess whether
an image contained a cancer. TCAV quantified the sensitivity of a
trained model to such concepts using concept activation vectors
(CAVs). The response of test cases to these CAVs was then used to
measure the sensitivity to that concept. The authors showed feasibility of TCAV on a medical image processing example, by relating physician annotations such as ‘microaneurysm’ to diabetic
retinopathy in fundus imaging.
Clough et al. (2019) identified cardiac disease in cine-MRI by
classifying the latent space of a VAE. They used TCAV to show
which clinically known biomarkers were related to cardiac disease.
Furthermore, they reconstructed images with low peak ejection
rate – a characteristic that might be related to cardiac disease –
by adding the CAV to the latent space.
Graziani et al. (2020) expanded on TCAV by introducing regression concept vectors. The main addition was that, while TCAV indicated the presence or absence of binary concepts, regression concept vectors indicated continuous-valued measures of a concept.
This can be useful when investigating a continuous concept such
as tumor size. Graziani et al. (2020) showed that by using regression concept vectors, they could for example explain why the network classified one area of a breast histopathology image as cancer
and another as healthy: Both areas of the image scored high on the
concept ‘contrast’, but the concept ‘nuclei area’, referring to a clinically used system for evaluating cell size, was different between
healthy and cancerous regions.
```

```
3.2.4. Other tel explanation techniques
Shen et al. (2019) used what they called a hierarchical semantic CNN to predict malignancy of lung nodules on CT. They classified five textual descriptions of image characteristics representative of lung nodule malignancy that are typically assessed by a
radiologist. The task of finding textual descriptions was combined
with the main task of classifying lung nodule malignancy. Although
their hierarchical semantic CNN did not significantly outperform a
normal CNN in predicting nodule malignancy, the method did provide human-interpretable characteristics of the nodules.
```


--------------------

**assistant**:
Based on the provided text, I have extracted the following facts related to the strategies for unraveling the "black-box" of AI-based Model-based explanation, focusing on the progress of Textual Explanation methods, specifically Image Captioning and Image Captioning with Visual Explanation. Here are the key findings in Markdown format:

### Image Captioning

- Vinyals et al. (2015) proposed an end-to-end image captioning framework that combined a convolutional neural network (CNN) for image encoding and a long-short term memory (LSTM) network for textual encoding. They used human-generated sentences as ground truth for training and the bilingual evaluation understudy (BLEU) metric for evaluation.

- Singh et al. (2019) used an image captioning framework to provide textual explanations for chest X-rays. They trained the LSTM using Global Vectors (GloVe) and the radiology variant RadGloVe, and evaluated their model using BLEU, METEOR, CIDER, and ROUGE metrics. They found that using both RadGloVe and GloVe led to higher performance in the generated radiology reports.

### Image Captioning with Visual Explanation

- Zhang et al. (2017a) introduced a framework that combined image captioning with visual explanation using dual attention for both text and imaging. This approach facilitated high-level interactions between image and text predictions, resulting in visual attention maps corresponding with textual explanations in histology images.

- Wang et al. (2018) used a similar approach for chest X-rays, showing that different parts of the textual explanation led to different areas of saliency mapping in the image. They demonstrated a saliency map of the chest with multiple regions corresponding to different radiological findings.

- Lee et al. (2019a) presented image captioning with visual explanation for breast mammograms. They added a visual word constraint loss to the text-generating LSTM to ensure that the provided explanations followed the correct jargon of breast mammography reports. They found that adding this loss improved the textual explanation quality and linked the radiology reports to visual saliency maps.

--------------------

**user**:
很棒！请依据上面的格式，继续提取TCAV和tel explanation两方面和主题相关的事实。你的回复应当是英文。
你给出事实的格式应当是：谁在什么文章中提出了什么理论、做出了什么工作。你需要紧紧围绕章节的主题。

--------------------

**assistant**:
Continuing with the provided text, I have extracted the following facts related to the strategies for unraveling the "black-box" of AI-based Model-based explanation, focusing on the progress of Textual Explanation methods, specifically Testing with Concept Activation Vectors (TCAV) and Other Textual Explanation Techniques. Here are the key findings in Markdown format:

### Testing with Concept Activation Vectors (TCAV)

- Kim et al. (2018) introduced TCAV, which provided human-friendly linear explanations of the internal state of neural networks in terms of human-understandable concepts. The TCAV algorithm used user-defined sets of examples of a concept and random non-concept examples. They demonstrated the feasibility of TCAV on a medical image processing example by relating physician annotations such as 'microaneurysm' to diabetic retinopathy in fundus imaging.

- Clough et al. (2019) used TCAV to identify cardiac disease in cine-MRI by classifying the latent space of a Variational Autoencoder (VAE). They showed which clinically known biomarkers were related to cardiac disease and reconstructed images with low peak ejection rate by adding the Concept Activation Vectors (CAVs) to the latent space.

- Graziani et al. (2020) expanded on TCAV by introducing regression concept vectors, which indicated continuous-valued measures of a concept. They demonstrated that using regression concept vectors could explain why the network classified one area of a breast histopathology image as cancer and another as healthy based on the concepts 'contrast' and 'nuclei area'.

### Other Textual Explanation Techniques

- Shen et al. (2019) used a hierarchical semantic CNN to predict malignancy of lung nodules on CT. They classified five textual descriptions of image characteristics representative of lung nodule malignancy typically assessed by a radiologist. Although their hierarchical semantic CNN did not significantly outperform a normal CNN in predicting nodule malignancy, the method provided human-interpretable characteristics of the nodules.