---
id: POL-16
title: Out-of-network requests
doc_type: policy
owner: Network Management
audience: PROVIDER_NURSE, PROVIDER_OFFICE_MGR, UM_NURSE
service_types: ALL
version: 1.8
effective_date: 2026-07-01
last_reviewed: 2026-08-26
related: WF-01, WF-06, UI-04, UI-10
---
# Out-of-network requests

This policy explains how Northwind handles prior-authorization requests where the servicing provider is outside the Northwind network. It covers the network adequacy exception and what happens when a request is denied with CR-ND-005.

## Does an out-of-network provider need an exception?
Yes. When the servicing provider on a prior-authorization request is not in the Northwind network, the request needs an approved network adequacy exception as well as the authorization itself. Without an approved exception, the request is denied with CR-ND-005, "Out-of-network without an approved exception". The exception is about where the service is delivered; it does not change the documentation the service type requires.

## What is a network adequacy exception?
A network adequacy exception is Northwind's approval for a member to receive a service from an out-of-network provider because no suitable in-network provider can deliver it. Common reasons are that no in-network provider offers the service within a reasonable distance, or that in-network providers cannot schedule it within a reasonable time. The exception is decided together with the prior-authorization request.

## How do I request a network adequacy exception?
Request the exception in the same intake request. On step **3 Providers**, enter the out-of-network servicing provider with a valid NPI. On step **4 Clinical**, state that a network adequacy exception is requested and why no in-network provider is suitable. Upload any supporting evidence, such as a list of in-network providers contacted and their responses, on step **5 Documents**. Do not include the member's name or address in file names.

## What can I do after a CR-ND-005 denial?
A CR-ND-005 denial is appealable. The office can file a first-level appeal within 60 calendar days of the denial, using **Appeal this decision**, with evidence that no suitable in-network provider was available. Alternatively, the office can submit a new request with an in-network servicing provider. A peer-to-peer is not offered for CR-ND-005; peer-to-peer applies only to CR-ND-004 and CR-ND-009. The service desk cannot grant a network adequacy exception.

## Does an out-of-network request route differently?
No. An out-of-network request is routed like any other, to the queue named `{REGION}-{SERVICE_TYPE}-{URGENCY}`. The region comes from the servicing provider's practice location. If an out-of-network servicing provider has no location on file, the request falls to `UNASSIGNED`, which the regional director sweeps every 24 hours. Entering a complete practice address for the provider avoids this delay. The review SLA still runs from submission while the request waits in `UNASSIGNED`.
