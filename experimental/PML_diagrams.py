import numpy as np
import numpy.random as rand
from scipy.stats import pearsonr
from matplotlib.pyplot import plot, axis, scatter, xlabel, ylabel, clabel, colorbar, text, subplot

rmsds = lambda gamma, R: np.sqrt(1. + gamma ** 2 - 2. * gamma * R)

class StatsDiagram:
    def __init__(self, data, refdata, *opts, **keys):
        dat = np.array(data).ravel()
        ref = np.array(refdata).ravel()
        self.std = ref.std()
        self.E0 = (dat - ref).mean() / self.std
        self.gamma = dat.std() / ref.std()
        self.R, self.p = pearsonr(dat, ref)
        self.E = rmsds(self.gamma, self.R)
        print(self)

    def __call__(self, data, refdata, *opts, **keys):
        dat = np.array(data).ravel()
        ref = np.array(refdata).ravel()
        self.std = ref.std()
        self.E0 = (dat - ref).mean() / self.std
        self.gamma = dat.std() / ref.std()
        self.R, self.p = pearsonr(dat, ref)
        self.E = rmsds(self.gamma, self.R)
        print(self)

    def __str__(self):
        return "\tNormalised Bias: " + str(self.E0) +\
               "\n\tNormalised Unbiased RMSD: " + str(self.E) +\
               "\n\tNormalised RMSD: " + str(np.sqrt(self.E0 ** 2 + self.E ** 2)) +\
               "\n\tCorrelation Coefficient: " + str(self.R) +\
               "\n\t\t with p-value: " + str(self.p) +\
               "\n\tSTD Ratio (Data/Reference): " + str(self.gamma) +\
               "\n\tReference STD: " + str(self.std) + '\n'


class Stats:
    def __init__(self, gam, E0, rho):
        self.E0 = E0
        self.R = rho
        self.gamma = gam
        self.E = rmsds(gam, rho)
        print(self)

    def __call__(self, gam, E0, rho):
        self.E0 = E0
        self.R = rho
        self.gamma = gam
        self.E = rmsds(gam, rho)
        print(self)

    def __str__(self):
        return "\tNormalised Bias: " + str(self.E0) +\
               "\n\tNormalised Unbiased RMSD: " + str(self.E) +\
               "\n\tNormalised RMSD: " + str(np.sqrt(self.E0 ** 2 + self.E ** 2)) +\
               "\n\tCorrelation Coefficient: " + str(self.R) +\
               "\n\tSTD Ratio (Data/Reference): " + str(self.gamma)


class Target:
    def drawTargetGrid(self):
        a = np.arange(0, 2.01 * np.pi, .02 * np.pi)
        plot(np.sin(a), np.cos(a), 'k')
        #radius at minimum RMSD' given R:
        #  Mr=sqrt(1+R^2-2R^2)
        #for R=0.7:
        plot(.71414284285428498 * np.sin(a), .71414284285428498 * np.cos(a), 'k--')
        #radius at observ. uncertainty:
        #plot(.5*sin(a),.5*cos(a),'k:')
        plot((0,), (0,), 'k+')
        ylabel('${Bias}/\sigma_{ref}$', fontsize=16)
        xlabel('${sign}(\sigma-\sigma_{ref})*{RMSD}\'/\sigma_{ref}$', fontsize=16)


class Taylor:
    def drawTaylorGrid(self, R, dr, antiCorrelation):
        if antiCorrelation:
            a0 = -1.
        else:
            a0 = 0.
            #Draw circles:
        a = np.arange(a0, 1.01, .05) * .5 * np.pi
        self.ax = plot(np.sin(a), np.cos(a), 'k-')
        plot(.5 * np.sin(a), .5 * np.cos(a), 'k:')
        n = R / .5
        for m in np.arange(3, n + 1):
            plot(m * .5 * np.sin(a), m * .5 * np.cos(a), 'k:')
            #Draw rays for correlations at .99,.75,.5,.25 steps:
        rays = list(np.arange(a0, 1.05, .25))
        rays.append(.99)
        if a0 == -1.: rays.append(-.99)
        for rho in rays:
            plot((R * rho, 0), (R * np.sin(np.arccos(rho)), 0), 'k:')
            d = rho >= 0. and 1.02 or 1.25
            text(d * R * rho, 1.01 * R * np.sin(np.arccos(rho)), str(rho), fontsize=8)
        text(1.01 * R * np.sin(np.pi * .25), 1.02 * R * np.cos(np.pi * .25), r'$\rho$', rotation=-45, fontsize=16)
        #text(0.,1.02*R*cos(0.),'0')
        #text(1.03*R*sin(.5*pi),0.,'1')
        goOn = True
        r = dr
        a = np.arange(-1., 1.01, .05) * .5 * np.pi
        plot((1,), (0,), 'ko')
        while goOn:
            xx = []
            yy = []
            for p in a:
                x = r * np.sin(p) + 1.
                y = r * np.cos(p)
                if antiCorrelation:
                    if x ** 2 + y ** 2 < R ** 2:
                        xx.append(x)
                        yy.append(y)
                else:
                    if x ** 2 + y ** 2 < R ** 2:
                        if x > 0.:
                            xx.append(x)
                            yy.append(y)
            if len(xx) > 0:
                plot(xx, yy, 'k--')
            else:
                goOn = False
            r += dr
        xlabel('$\sigma/\sigma_{ref}$', fontsize=16)
        ylabel('$\sigma/\sigma_{ref}$', fontsize=16)


class TaylorDiagram(Taylor, Stats):
    def __init__(self, gam, E0, rho, R=2.5, dr=.5, antiCorrelation=True, marker='o', s=40, *opts, **keys):
        Stats.__init__(self, gam, E0, rho)
        R = max(int(2. * self.gamma + 1.) / 2., 1.5)
        self.drawTaylorGrid(R, dr, antiCorrelation)
        self._cmax = max(1., abs(self.E0))
        self._cmin = -self._cmax
        self._lpos = []
        if antiCorrelation:
            self._axis = {'xmin': -1.3 * R, 'xmax': 1.3 * R, 'ymin': -.1 * R, 'ymax': 1.1 * R}
        else:
            self._axis = {'xmin': -.1 * R, 'xmax': 1.3 * R, 'ymin': -.1 * R, 'ymax': 1.1 * R}
        self.add(self.gamma, self.E0, self.R, marker=marker, s=s, *opts, **keys)
        self.cbar = colorbar()
        self.cbar.set_label('${Bias}/\sigma_{ref}$')

    def __call__(self, gam, E0, rho, marker='o', s=40, *opts, **keys):
        self._cmax = max(abs(E0), self._cmax)
        self._cmin = -self._cmin
        Stats.__call__(self, gam, E0, rho)
        self.add(gam, E0, rho, marker=marker, s=s, *opts, **keys)

    def add(self, gam, E0, R, marker='o', s=40, *opts, **keys):
        E = rmsds(gam, R)
        scatter(gam * R, gam * np.sin(np.arccos(R)), c=E0, vmin=self._cmin, vmax=self._cmax, marker=marker, s=s, *opts,
            **keys)
        self._lpos.append((gam * R, gam * np.sin(np.arccos(R))))
        axis(**self._axis)

    def labels(self, lstr, *opts, **keys):
        yrange = axis()[2:]
        rmax = abs(yrange[1] - yrange[0])
        for n, p in enumerate(self._lpos):
            text(p[0] + .025 * rmax, p[1] + .025 * rmax, lstr[n], *opts, **keys)


class TargetDiagram(Target, Stats):
    def __init__(self, gam, E0, rho, marker='o', s=40, antiCorrelation=False, *opts, **keys):
        Stats.__init__(self, gam, E0, rho)
        self.drawTargetGrid()
        if antiCorrelation:
            self._cmin = -1.
        else:
            self._cmin = 0.
        self._cmax = 1.
        self._lpos = []
        self.add(self.gamma, self.E0, self.R, marker=marker, s=s, *opts, **keys)
        self.cbar = colorbar()
        self.cbar.set_label('Correlation Coefficient')

    def __call__(self, gam, E0, rho, marker='o', s=40, *opts, **keys):
        Stats.__call__(self, gam, E0, rho)
        self.add(self.gamma, self.E0, self.R, marker=marker, s=s, *opts, **keys)

    def add(self, gam, E0, R, marker='o', s=40, *opts, **keys):
        sig = gam.all() > 1 and 1 or -1
        E = rmsds(gam, R)
        scatter(sig * E, E0, vmin=self._cmin, vmax=self._cmax, marker=marker, s=s, *opts, **keys)
        self._lpos.append((sig * E, E0))
        rmax = np.max(np.abs(np.array(axis('scaled'))))
        plot((0, 0), (-rmax, rmax), 'k-')
        plot((rmax, -rmax), (0, 0), 'k-')
        axis(xmin=-rmax, xmax=rmax, ymax=rmax, ymin=-rmax)

    def labels(self, lstr, *opts, **keys):
        rmax = np.max(np.abs(np.array(axis())))
        for n, p in enumerate(self._lpos):
            text(p[0] + .025 * rmax, p[1] + .025 * rmax, lstr[n], *opts, **keys)


class TargetStatistics(StatsDiagram, TargetDiagram):
    def __init__(self, data, refdata, marker='o', s=40, antiCorrelation=False, *opts, **keys):
        StatsDiagram.__init__(self, data, refdata, *opts, **keys)
        self.drawTargetGrid()
        if antiCorrelation:
            self._cmin = -1.
        else:
            self._cmin = 0.
        self._cmax = 1.
        self._lpos = []
        self.add(self.gamma, self.E0, self.R, marker=marker, s=s, *opts, **keys)
        self.cbar = colorbar()
        self.cbar.set_label('Correlation Coefficient')

    def __call__(self, data, refdata, marker='o', s=40, *opts, **keys):
        StatsDiagram.__call__(self, data, refdata, *opts, **keys)
        self.add(self.gamma, self.E0, self.R, marker=marker, s=s, *opts, **keys)

    def add(self, gam, E0, R, marker='o', s=40, *opts, **keys):
        sig = gam > 1 and 1 or -1
        E = np.sqrt(1. + gam ** 2 - 2. * gam * R)
        scatter(sig * E, E0, c=R, vmin=self._cmin, vmax=self._cmax, marker=marker, s=s, *opts, **keys)
        self._lpos.append((sig * E, E0))
        rmax = np.max(np.abs(np.array(axis('scaled'))))
        plot((0, 0), (-rmax, rmax), 'k-')
        plot((rmax, -rmax), (0, 0), 'k-')
        axis(xmin=-rmax, xmax=rmax, ymax=rmax, ymin=-rmax)

    def labels(self, lstr, *opts, **keys):
        rmax = np.max(np.abs(np.array(axis())))
        for n, p in enumerate(self._lpos):
            text(p[0] + .025 * rmax, p[1] + .025 * rmax, lstr[n], *opts, **keys)


class TaylorStatistics(StatsDiagram, TaylorDiagram):
    def __init__(self, data, refdata, R=2.5, dr=.5, antiCorrelation=True, marker='o', s=40, *opts, **keys):
        StatsDiagram.__init__(self, data, refdata, *opts, **keys)
        R = max(int(2. * self.gamma + 1.) / 2., 1.5)
        self.drawTaylorGrid(R, dr, antiCorrelation)
        self._cmax = max(1., abs(self.E0))
        self._cmin = -self._cmax
        self._lpos = []
        if antiCorrelation:
            self._axis = {'xmin': -1.3 * R, 'xmax': 1.3 * R, 'ymin': -.1 * R, 'ymax': 1.1 * R}
        else:
            self._axis = {'xmin': -.1 * R, 'xmax': 1.3 * R, 'ymin': -.1 * R, 'ymax': 1.1 * R}
        self.add(self.gamma, self.E0, self.R, marker=marker, s=s, *opts, **keys)
        self.cbar = colorbar()
        self.cbar.set_label('${Bias}/\sigma_{ref}$')

    def __call__(self, data, refdata, marker='o', s=40, *opts, **keys):
        StatsDiagram.__call__(self, data, refdata, *opts, **keys)
        self._cmax = max(abs(self.E0), self._cmax)
        self._cmin = -self._cmax
        self.add(self.gamma, self.E0, self.R, marker=marker, s=s, *opts, **keys)

#Examples:

a = rand.random(10)
b = rand.random(10)
ref = rand.random(10)
subplot(221)
TD = TargetDiagram(a, ref, 0.5)
TD(b, ref)
subplot(222)
TD = TaylorDiagram(a, ref, 0.5)
TD(b, ref)

#R1,p=pearsonr(a,ref)
#E1=a.mean()-ref.mean()
#std1=a.std()
#refstd1=ref.std()
#R2,p=pearsonr(b,ref)
#E2=b.mean()-ref.mean()
#std2=b.std()
#refstd2=ref.std()

#subplot(223)
#TD=TargetPlot(R1,E1,std1,refstd1)
#TD(R2,E2,std2,refstd2)
#subplot(224)
#TD=TaylorPlot(R1,E1,std1,refstd1)
#TD(R2,E2,std2,refstd2)


