%module Cg
%{
#include <cg.h>
%}

// context functions
CGcontext cgCreateContext(void);
void cgDestroyContext(CGcontext);
int cgIsContext(CGcontext);
char *cgGetLastListing(CGcontext);

// program functions
CGprogram cgCreateProgram(CGcontext, CGenum, const char *, CGprofile, const char *,  const char **);
CGprogram cgCreateProgramFromFile(CGcontext, CGenum, const char *, CGprofile, const char *, const char **);
CGprogram cgCopyProgram(CGprogram);
void cgDestroyProgram(CGprogram);
CGprogram cgGetFirstProgram(CGcontext);
CGprogram cgGetNextProgram(CGprogram);
CGcontext cgGetProgramContext(CGprogram);
int cgIsProgram(CGprogram);
void cgCompileProgram(CGprogram);
int cgIsProgramCompiled(CGprogram);
const char *cgGetProgramString(CGprogram, CGenum);
CGprofile cgGetProgramProfile(CGprogram);

// parameter functions
CGparameter cgGetNamedParameter(CGprogram, const char *);
CGparameter cgGetFirstParameter(CGprogram, CGenum);
CGparameter cgGetNextParameter(CGparameter);
CGparameter cgGetFirstLeafParameter(CGprogram, CGenum);
CGparameter cgGetNextLeafParameter(CGparameter);
CGparameter cgGetFirstStructParameter(CGparameter);
CGparameter cgGetFirstDependentParameter(CGparameter);
CGparameter cgGetArrayParameter(CGparameter, int);
int cgGetArrayDimension(CGparameter);
int cgGetArraySize(CGparameter, int);
CGprogram cgGetParameterProgram(CGparameter prog);
int cgIsParameter(CGparameter);
const char *cgGetParameterName(CGparameter);
CGtype cgGetParameterType(CGparameter);
const char *cgGetParameterSemantic(CGparameter);
CGresource cgGetParameterResource(CGparameter);
CGresource cgGetParameterBaseResource(CGparameter);
unsigned long cgGetParameterResourceIndex(CGparameter);
CGenum cgGetParameterVariability(CGparameter);
CGenum cgGetParameterDirection(CGparameter);
int cgIsParameterReferenced(CGparameter);
const double *cgGetParameterValues(CGparameter, CGenum, int *);
int cgGetParameterOrdinalNumber(CGparameter);

// type functions
const char *cgGetTypeString(CGtype);
CGtype cgGetType(const char *);

// resource functions
const char *cgGetResourceString(CGresource);
CGresource cgGetResource(const char *);

// profile functions
const char *cgGetProfileString(CGprofile);
CGprofile cgGetProfile(const char *);

// error functions
CGerror cgGetError(void);
const char *cgGetErrorString(CGerror);
void cgSetErrorCallback(CGerrorCallbackFunc);
CGerrorCallbackFunc cgGetErrorCallback();