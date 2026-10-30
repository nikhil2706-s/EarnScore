export function saveSessionAssessment(records, assessment, financialData = null) {
  const applicantId = assessment?.applicant_id;

  if (typeof applicantId !== 'string' || !applicantId.trim()) {
    throw new Error('Scoring response is missing applicant_id');
  }

  const existing = records.find(
    record => record.applicantId === applicantId
  );

  const updated = {
    applicantId,
    assessment,
    financialData,
    review: existing?.review ?? null,
    updatedAt: new Date().toISOString(),
  };

  return [
    updated,
    ...records.filter(record => record.applicantId !== applicantId),
  ];
}

export function filterSessionAssessments(
  records,
  searchQuery = '',
  statusFilter = 'all',
  riskFilter = 'all'
) {
  const query = searchQuery.trim().toLowerCase();

  return records.filter(record => {
    const matchesSearch =
      record.applicantId.toLowerCase().includes(query);

    const status = record.review?.status ?? 'pending';
    const matchesStatus =
      statusFilter === 'all' || status === statusFilter;

    const band = String(record.assessment?.band ?? '')
      .toLowerCase()
      .replace(/\s+/g, '_');

    const matchesRisk =
      riskFilter === 'all' || band === riskFilter;

    return matchesSearch && matchesStatus && matchesRisk;
  });
}
