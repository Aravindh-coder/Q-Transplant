export function renderQRBadge(donorToken = "QR-DONOR-O-PLUS-001", donorName = "David Miller") {
  return `
    <div class="bx--tile" style="border: 1px dashed var(--cds-interactive-01); text-align: center; padding: 1.5rem;">
      <div class="bx--tile__heading" style="margin-bottom: 8px;"><i class="fa-solid fa-qrcode"></i> OFFICIAL DONOR QR IDENTIFICATION BADGE</div>
      <div style="background: #ffffff; padding: 15px; display: inline-block; border-radius: 8px; margin: 10px 0;">
        <!-- Embedded SVG QR Code representation -->
        <svg width="120" height="120" viewBox="0 0 100 100" fill="#000000">
          <rect x="0" y="0" width="30" height="30"/>
          <rect x="5" y="5" width="20" height="20" fill="#ffffff"/>
          <rect x="10" y="10" width="10" height="10"/>
          
          <rect x="70" y="0" width="30" height="30"/>
          <rect x="75" y="5" width="20" height="20" fill="#ffffff"/>
          <rect x="80" y="10" width="10" height="10"/>
          
          <rect x="0" y="70" width="30" height="30"/>
          <rect x="5" y="75" width="20" height="20" fill="#ffffff"/>
          <rect x="10" y="80" width="10" height="10"/>
          
          <rect x="40" y="10" width="15" height="15"/>
          <rect x="40" y="40" width="20" height="20"/>
          <rect x="70" y="40" width="15" height="15"/>
          <rect x="10" y="45" width="15" height="15"/>
          <rect x="50" y="70" width="20" height="20"/>
          <rect x="80" y="80" width="15" height="15"/>
        </svg>
      </div>
      <div style="font-weight: 600; font-size: 14px; color: var(--cds-text-01);">${donorName}</div>
      <div style="font-family: var(--cds-mono-font); font-size: 12px; color: var(--cds-interactive-01);">${donorToken}</div>
      <div style="font-size: 11px; color: var(--cds-text-03); margin-top: 6px;">Scannable by Authorized Hospital Trauma Teams</div>
    </div>
  `;
}
