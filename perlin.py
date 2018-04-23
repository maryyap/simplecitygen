import math

p = [151,160,137,91,90,15,
  131,13,201,95,96,53,194,233,7,225,140,36,103,30,69,142,8,99,37,240,21,10,23,
  190, 6,148,247,120,234,75,0,26,197,62,94,252,219,203,117,35,11,32,57,177,33,
  88,237,149,56,87,174,20,125,136,171,168, 68,175,74,165,71,134,139,48,27,166,
  77,146,158,231,83,111,229,122,60,211,133,230,220,105,92,41,55,46,245,40,244,
  102,143,54, 65,25,63,161, 1,216,80,73,209,76,132,187,208, 89,18,169,200,196,
  135,130,116,188,159,86,164,100,109,198,173,186, 3,64,52,217,226,250,124,123,
  5,202,38,147,118,126,255,82,85,212,207,206,59,227,47,16,58,17,182,189,28,42,
  223,183,170,213,119,248,152, 2,44,154,163, 70,221,153,101,155,167, 43,172,9,
  129,22,39,253, 19,98,108,110,79,113,224,232,178,185, 112,104,218,246,97,228,
  251,34,242,193,238,210,144,12,191,179,162,241, 81,51,145,235,249,14,239,107,
  49,192,214, 31,181,199,106,157,184, 84,204,176,115,121,50,45,127, 4,150,254,
  138,236,205,93,222,114,67,29,24,72,243,141,128,195,78,66,215,61,156,180]

class Grad():
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def dot2(self, x, y):
        return self.x * x + self.y * y

    def dot3(self, x, y, z):
        return self.x * x + self.y * y + this.z * z

grad3 = [Grad(1,1,0),Grad(-1,1,0),Grad(1,-1,0),Grad(-1,-1,0),
             Grad(1,0,1),Grad(-1,0,1),Grad(1,0,-1),Grad(-1,0,-1),
             Grad(0,1,1),Grad(0,-1,1),Grad(0,1,-1),Grad(0,-1,-1)]

class Perlin():
    def __init__(self, seed = 0):
        self.perm = [0] * 512
        self.gradP = [0] * 512
        self.f2 = 0.5 * (math.sqrt(3) - 1)
        self.g2 = (3 - math.sqrt(3)) / 6
        self.f3 = 1.0 / 3
        self.g3 = 1.0 / 6

        if (seed >= 0 and seed <= 1):
            seed = seed * 65536

        seed = int(math.floor(seed))
        if (seed < 256):
            seed = seed | (seed << 8)

        for i in range(256):
            if (i & 1):
                v = p[i] ^ (seed & 255)
            else:
                v = p[i] ^ ((seed >> 8) & 255)

            self.perm[i] = self.perm[i + 256] = v
            self.gradP[i] = self.gradP[i + 256] = grad3[v % 12]

    def simplex2(self, xin, yin):
        s = (xin + yin) * self.f2
        i = int(math.floor(xin + s))
        j = int(math.floor(yin + s))
        t = (i + j) * self.g2
        x0 = xin - i + t
        y0 = yin - j + t

        if (x0 > y0):
            i1 = 1
            j1 = 0
        else:
            i1 = 0
            j1 = 1

        x1 = x0 - i1 + self.g2
        y1 = y0 - j1 + self.g2
        x2 = x0 - 1 + 2 * self.g2
        y2 = y0 - 1 + 2 * self.g2

        i = i & 255
        j = j & 255

        gi0 = self.gradP[i+self.perm[j]]
        gi1 = self.gradP[i+i1+self.perm[j+j1]]
        gi2 = self.gradP[i+1+self.perm[j+1]]

        t0 = 0.5 - x0*x0-y0*y0
        if (t0 < 0):
          n0 = 0
        else:
          t0 *= t0
          n0 = t0 * t0 * gi0.dot2(x0, y0)

        t1 = 0.5 - x1*x1-y1*y1
        if(t1 < 0):
          n1 = 0
        else:
          t1 *= t1
          n1 = t1 * t1 * gi1.dot2(x1, y1)

        t2 = 0.5 - x2*x2-y2*y2
        if (t2 < 0):
          n2 = 0
        else:
          t2 *= t2
          n2 = t2 * t2 * gi2.dot2(x2, y2)

        return 70 * (n0 + n1 + n2)
