# FRIDGE: Federated Research Infrastructure by Data Governance Extension

This repository contains the code and documentation for FRIDGE, a DARE UK Early Adopter project aimed at extending the capabilities of Trusted Research Environments (TREs) to leverage the computational resources of the national AI Research Resource (AIRR).

## Overview

FRIDGE will provide a framework for securely accessing and processing sensitive data on AIRR from within an existing TRE.
The technical side of the project is built on Kubernetes, allowing portability across different cloud providers and on-premises installations.
The project also focuses on ensuring compliance with data governance and security policies.

In this repository, you will find various modules and components that make up a FRIDGE deployment.
We provide infrastructure-as-code to deploy FRIDGE to suitably configured infrastructure no Dawn AI, Isambard AI, and Azure Kubernetes Service (AKS).
In addition, we provide infrastructure-as-code for deploying suitable infrastructure for FRIDGE on Azure Kubernetes Service (AKS).

You will require Pulumi to deploy the infrastructure.

For more detailed information, please visit the project website: https://alan-turing-institute.github.io/fridge/
