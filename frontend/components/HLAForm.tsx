import React from 'react';

export interface HLAAlleles {
  hla_a1: string;
  hla_a2: string;
  hla_b1: string;
  hla_b2: string;
  hla_dr1: string;
  hla_dr2: string;
}

interface HLAFormProps {
  values: HLAAlleles;
  onChange: (field: keyof HLAAlleles, val: string) => void;
}

export const HLAForm: React.FC<HLAFormProps> = ({ values, onChange }) => {
  const fields: { key: keyof HLAAlleles; label: string; placeholder: string }[] = [
    { key: 'hla_a1', label: 'HLA-A Allele 1', placeholder: 'e.g. A*02:01' },
    { key: 'hla_a2', label: 'HLA-A Allele 2', placeholder: 'e.g. A*24:02' },
    { key: 'hla_b1', label: 'HLA-B Allele 1', placeholder: 'e.g. B*07:02' },
    { key: 'hla_b2', label: 'HLA-B Allele 2', placeholder: 'e.g. B*44:02' },
    { key: 'hla_dr1', label: 'HLA-DR Allele 1', placeholder: 'e.g. DRB1*04:01' },
    { key: 'hla_dr2', label: 'HLA-DR Allele 2', placeholder: 'e.g. DRB1*15:01' },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4 rounded-xl bg-slate-950/40 border border-indigo-500/20">
      <div className="col-span-full mb-1">
        <h4 className="text-sm font-semibold text-indigo-300 uppercase tracking-wider">
          6-Allele HLA Immunological Profile
        </h4>
        <p className="text-xs text-slate-400">
          Encrypted with AES-256 before quantum state bitstring encoding.
        </p>
      </div>

      {fields.map(({ key, label, placeholder }) => (
        <div key={key}>
          <label className="block text-xs font-medium text-slate-300 mb-1">{label}</label>
          <input
            type="text"
            value={values[key]}
            onChange={(e) => onChange(key, e.target.value)}
            placeholder={placeholder}
            className="w-full px-3 py-2 text-sm bg-slate-900/80 border border-slate-700/60 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
          />
        </div>
      ))}
    </div>
  );
};
