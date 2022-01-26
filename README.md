# buildConnectome-ACT-SIFT2
This repository compares the connectomes estimated with two different tractography pipelines on a group of subjects affected by the Fabry disease. The estimated connectomes are analyzed by means of the 3 network metrics.

The first pipeline uses Anatomically Constrained Tractography (ACT) and the connectivity between every pair of cortical regions is "quantified" by means of the number of streamlines connecting them.
The second pipeline uses the SIFT2 filtering technique in order to estimate the actual contribution/weight of each streamline, i.e. attempts to obtain quantitative information from tractography. In this case, the connectivity is "quantified" by means of the weights returned by SIFT2 and using the previous tractogram to identify the streamlines connecting every pair of regions.

Both techniques are implemented in the MrTrix toolbox.  The goal is to study whether the two approaches for building the connectomes (1 using the streamline count and the second one using the weights estimated with SIFT2) are able to differentiate the two groups of subjects (patients vs controls) based on such network properties.
