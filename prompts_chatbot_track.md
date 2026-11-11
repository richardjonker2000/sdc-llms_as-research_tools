# Chatbot track: the same demos, no code

For participants without Python. Use any chatbot in your browser: **Doubao (豆包), Kimi, DeepSeek, Qwen (通义) or ChatGPT**. Copy each grey box into a **new chat**, run it, and compare your answers with your neighbours'. Differences between chatbots are part of the lesson.

---

## Demo 1 · Codebook extraction (matches notebook 01)

Copy the whole box, including the five abstracts. They are real US patents (public domain).

```text
You are a research assistant coding patent abstracts for an innovation study.
Code each of the 5 abstracts below with this codebook. Answer as a table with one row per patent.

CODEBOOK
- is_ai: yes/no. Yes if the invention uses or improves artificial intelligence or machine learning.
- technology: the core technology in 2 to 5 words.
- problem_solved: the problem the invention solves, in one short sentence.
- application_domain: exactly one of: health, finance, manufacturing, transport, energy, retail & consumer, ICT & telecom, other.
- automation_vs_augmentation: exactly one of: automates human work, augments human work, neither.
- evidence_quote: a short phrase copied WORD FOR WORD from the abstract that supports is_ai.

ABSTRACTS
[P1] US12079712B2 (Sony Semiconductor Solutions): A solid-state image capturing system (1) includes a solid-state image capturing device (100) and an information processing device (200). The solid-state image capturing device (100) includes a first DNN processing unit (130) that executes, on image data, a part of a DNN algorithm by a first DNN to generate a first result. The information processing device (200) includes a second DNN processing unit (230) that executes, on the first result acquired from the solid-state image capturing device, remaining of the DNN algorithm by a second DNN to generate a second result.

[P2] US11966816B2 (Virginia Tech): Aspects of generating error-resistant quantum control pulses from geometrical curves are described. In some embodiments, a closed space curve is parameterized for a target gate operation of a quantum computing device. The closed space curve corresponds to an evolution operator of a time-dependent Schrödinger equation associated with the target gate operation. A control field definition is identified for the target gate operation based at least in part on a geometrical analysis of the evolution operator of the time-dependent Schrödinger equation. The target gate operation is implemented for the quantum computing device based on the control field definition.

[P3] US11276140B2 (Robert Bosch): Computer implemented method for digital image data, digital video data or digital audio data enhancement, and a computer implemented method for encoding or decoding this data in particular for transmission or storage, wherein an element representing a part of said digital data comprises an indication of a position of the element in an ordered input data of a plurality of data elements, wherein a plurality of elements is transformed to a representation depending on an invertible linear mapping, wherein the invertible linear mapping maps the input of the plurality of elements to the representation, wherein the invertible linear mapping comprises at least one autoregressive convolution.

[P4] US12051871B2 (Foxconn Kunshan): An electrical connector includes an insulative housing defining a channel and plural contacts secured to the insulative housing, each contact having a first arm exposed to the channel, a second arm exposed to the channel, a bottom arm connected to the first and second arms, and a soldering portion connected to the bottom arm.

[P5] US11985910B2 (Samsung Electronics): Provided are memristors and neuromorphic devices including the memristors. A memristor includes a lower electrode and an upper electrode that are apart from each other and first and second two-dimensional material layers that are arranged between the lower electrode and the upper electrode and stacked without a chemical bond therebetween.
```

**Then check:** search each `evidence_quote` in the abstract (Ctrl+F). Is it really there, word for word? Patents P2, P3 and P5 are genuinely hard to call. Did your chatbot agree with your neighbour's?

---

## Demo 2 · Consistency (matches notebook 02)

Paste this prompt, then click **regenerate** (or paste it again in a new chat) two or three times. Do the labels change?

```text
Classify each work task for exposure to large language models (LLMs).
high: an LLM alone could do most of this task today, because it is mainly reading, writing or analysing text or data.
medium: an LLM could do part of the task, or could do it only with extra tools, data access or human checks.
low: the task is mainly physical or in-person, or depends on presence, relationships or formal authority.
Answer with a table: task number, label, one-sentence reason.

1. Review financial statements, sales or activity reports, or other performance data to measure productivity or goal achievement or to identify areas needing cost reduction or program improvement.
2. Prepare staff work schedules and assign specific duties.
3. Prepare reports of findings, illustrating data graphically and translating complex findings into written text.
4. Supervise auditing of establishments, and determine scope of investigation required.
5. Confer with data processing or project managers to obtain information on limitations or capabilities for data processing projects.
6. Gather and analyze research data, such as statutes, decisions, and legal articles, codes, and documents.
```

The tasks come from O\*NET 31.0 (USDOL/ETA, CC BY 4.0). Tasks whose label changes between regenerations are the ambiguous ones. Would two human coders agree on them?

---

## Demo 3 · Long text: extract, then aggregate (matches notebook 04)

Open any trial on clinicaltrials.gov, copy its **Eligibility Criteria** section, and paste it after this prompt:

```text
Extract the eligibility rules of this clinical trial. Use only what the text says. Answer in exactly this format:
min_age: <years or "not stated">
max_age: <years or "no limit">
conditions_excluded: <up to 8 short generic names, lower case, comma-separated>
requires_prior_treatment: <yes/no>

TEXT:
<paste here>
```

Then compare your result with the age shown at the top of the trial page. Collect results from your table and count the exclusions together. That is the aggregation step.

---

## Demo 4 · Rewriting (matches notebook 05)

**(a) Clean firm names**

```text
For each patent assignee name below, give the short name of its parent company or group. Answer as a two-column table.
KABUSHIKI KAISHA TOSHIBA
Toshiba Tec Kabushiki Kaisha
TOSHIBA MEMORY CORPORATION
LG Energy Solution, Ltd.
LG ELECTRONICS INC.
LG DISPLAY CO., LTD.
Siemens Healthineers AG
SIEMENS AKTIENGESELLSCHAFT
TOYOTA JIDOSHA KABUSHIKI KAISHA
Toyota Research Institute, Inc.
Sony Group Corporation
SONY SEMICONDUCTOR SOLUTIONS CORPORATION
```

**(b) Translate and keep the voice.** The quote is synthetic.

```text
Translate this interview quote from Chinese into English. Keep the speaker's register: if they sound casual, blunt or frustrated, the English should too. Return only the translation.

系统让你几点到你就得几点到，下雨也一样。我跟站长李强说过好几次了，算法根本不知道小区门口不让电动车进。他说他也没办法，都是总部定的。
```

Now ask the same chatbot for a "formal, neutral translation" and compare. What gets lost?

**(c) Anonymise.** The quote is synthetic, and all names are fictional.

```text
Rewrite the interview quote below. Replace every person's name with [PERSON], every company or organisation with [ORG], and every city, region or country with [PLACE]. Change nothing else.

At Hongqiao Precision Parts we use the chatbot for first-round CV screening now. Ms. Zhou in recruitment still reads every rejected file from our Suzhou plant, because we worry about bias against older applicants.
```

Check: did anything identifying survive?

---

## Demo 5 · Your own text

```text
You are coding short research texts. For each text below, fill in:
- topic: work & labour / trade & policy / innovation & R&D / finance / other
- actor: the main firm, group or institution, in 1-4 words
- tone: positive / negative / mixed / neutral
- evidence_quote: a short phrase copied word for word from the text
Answer as a table.

TEXTS:
<paste 3-5 short texts, one per line, e.g. from an interview or a news article>
```

**Reminder:** anything you paste into a chatbot leaves your computer. Don't paste confidential or personal data.
