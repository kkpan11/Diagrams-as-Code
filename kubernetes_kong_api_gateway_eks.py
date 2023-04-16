#!/usr/bin/env python3
#  coding=utf-8
#  vim:ts=4:sts=4:sw=4:et
#
#  Author: Hari Sekhon
#  Date: 2023-04-15 22:35:45 +0100 (Sat, 15 Apr 2023)
#
#  https://github.com/HariSekhon/Diagrams-as-Code
#
#  License: see accompanying Hari Sekhon LICENSE file
#
#  If you're using my code you're welcome to connect with me on LinkedIn
#  and optionally send me feedback to help steer this or other code I publish
#
#  https://www.linkedin.com/in/HariSekhon
#

"""

Kong API Gateway on Kubernetes (AWS EKS)

"""

__author__ = 'Hari Sekhon'
__version__ = '0.1'

from diagrams import Diagram, Cluster, Edge

# On-premise / Open Source resources:
#
#   https://diagrams.mingrammer.com/docs/nodes/onprem
#
from diagrams.onprem.network import Kong
from diagrams.onprem.certificates import CertManager, LetsEncrypt
from diagrams.onprem.vcs import Github
from diagrams.onprem.gitops import ArgoCD
from diagrams.onprem.client import Users

# K8s resources:
#
#   https://diagrams.mingrammer.com/docs/nodes/k8s
#
from diagrams.k8s.compute import Pod
from diagrams.k8s.network import Ingress, Service

# AWS resources:
#
#   https://diagrams.mingrammer.com/docs/nodes/aws
#
from diagrams.aws.compute import EKS
from diagrams.aws.network import ELB, Route53

# pylint: disable=W0104,W0106
with Diagram('Kubernetes Kong API Gateway AWS',
             show=True,
             direction='TB',
             ):

    letsencrypt = LetsEncrypt("LetsEncrypt Certificate Authority")
    users = Users("Users")
    github = Github("GitHub")

    with Cluster("AWS"):
        elb = ELB("ELB Load Balancer")
        route53 = Route53("Route53 DNS")
        elb - route53
        users >> Edge(label="HTTPS traffic") >> elb
        users >> Edge(label="DNS queries") >> route53

        with Cluster("Kubernetes Cluster"):
            eks = EKS("EKS")
            with Cluster("Cert Manager"):
                certmanager = CertManager("Cert Manager")
            with Cluster("ArgoCD"):
                argocd = ArgoCD("ArgoCD")
            with Cluster("Ingress"):
                kong = Kong("Kong API Gateway\nIngress Controller")
                ingress = Ingress("Kubernetes Ingress")
            letsencrypt >> Edge(label="ACME protocol\ngenerated certificate", style="dashed") >> certmanager
            certmanager >> Edge(label="SSL cert", style="dashed") >> ingress
            ingress - kong
            github >> Edge(label="GitOps trigger", style="dashed") >> argocd
            # argocd >> Edge(label="updates", style="dashed") >> ingress
            argocd >> Edge(style="dashed") >> ingress

            with Cluster("WebApp 2"):
                service = Service("WebApp 2 Service")
                kong >> service
                pods = []
                for _ in range(3, 0, -1):
                    pods.append(Pod(f"Pod {_}") << service)
                #     argocd >> service
                # argocd >> pods

            with Cluster("WebApp 1"):
                service = Service("WebApp 1 Service")
                kong >> service
                pods = []
                for _ in range(3, 0, -1):
                    pods.append(Pod(f"Pod {_}") << service)
                #     argocd >> service
                # argocd >> pods

        elb >> ingress